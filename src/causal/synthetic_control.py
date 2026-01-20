"""
Synthetic Control Method for Causal Attribution

Synthetic Control estimates causal effects by constructing a weighted
combination of control units that matches the treated unit's
pre-treatment trajectory.

Key Idea:
- We observe one treated unit (e.g., region where we launched campaign)
- We have multiple control units (regions without campaign)
- We weight controls to match treated unit's pre-treatment behavior
- Post-treatment difference = causal effect

Examples in Marketing:
- Effect of launching in a new market (control: similar markets)
- Impact of major campaign (control: similar time periods)
- Store opening effects (control: similar stores)

Requirements:
- Multiple potential control units (donor pool)
- Pre-treatment period where we observe both treated and controls
- Treatment occurs at a specific point in time

Usage:
    sc = SyntheticControlEstimator(
        treated_outcomes, control_outcomes, treatment_time
    )
    result = sc.estimate_treatment_effect()
"""

import numpy as np
from scipy import optimize
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SyntheticControlResult:
    """Results from synthetic control estimation."""
    # Causal estimates
    treatment_effect: float  # Average post-treatment effect
    cumulative_effect: float  # Sum of all post-treatment effects
    effects_by_period: List[float]  # Effect for each post-treatment period

    # Synthetic control composition
    weights: Dict[str, float]  # Control unit weights
    n_controls_used: int  # Number of controls with weight > 0.01

    # Fit quality
    pre_treatment_rmse: float  # How well synthetic matches pre-treatment
    pre_treatment_correlation: float

    # Inference
    p_value: float  # Placebo-based p-value
    confidence_interval: Tuple[float, float]

    # Time periods
    treatment_time: int
    n_pre_periods: int
    n_post_periods: int

    def __repr__(self):
        top_weights = sorted(
            self.weights.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        weights_str = ", ".join(f"{k}: {v:.2f}" for k, v in top_weights)

        return f"""SyntheticControlResult(
    Average Treatment Effect:  {self.treatment_effect:.4f}
    Cumulative Effect:         {self.cumulative_effect:.4f}
    P-value (placebo):         {self.p_value:.3f}
    95% CI:                    [{self.confidence_interval[0]:.4f}, {self.confidence_interval[1]:.4f}]

    Pre-treatment RMSE:        {self.pre_treatment_rmse:.4f}
    Pre-treatment Corr:        {self.pre_treatment_correlation:.3f}

    Treatment time:            {self.treatment_time}
    Pre-periods:               {self.n_pre_periods}
    Post-periods:              {self.n_post_periods}

    Top weights: {weights_str}
    Controls used: {self.n_controls_used}
)"""


class SyntheticControlEstimator:
    """
    Synthetic Control Method estimator.

    Constructs a weighted combination of control units to approximate
    the treated unit's counterfactual (what would have happened without treatment).

    Parameters
    ----------
    treated : np.ndarray
        Outcome time series for treated unit (T periods)
    controls : np.ndarray or dict
        Outcome time series for control units
        Shape: (T periods, N control units) or dict {name: array}
    treatment_time : int
        Index of first treatment period (0-indexed)
    control_names : list, optional
        Names for control units

    Example
    -------
    >>> # Effect of launching marketing campaign in California
    >>> sc = SyntheticControlEstimator(
    ...     treated=california_sales,      # Monthly sales
    ...     controls=other_states_sales,   # Matrix of other states
    ...     treatment_time=24              # Campaign started month 24
    ... )
    >>> result = sc.estimate_treatment_effect()
    >>> print(f"Campaign effect: {result.treatment_effect:.1%} lift")
    """

    def __init__(
        self,
        treated: np.ndarray,
        controls: np.ndarray,
        treatment_time: int,
        control_names: Optional[List[str]] = None
    ):
        self.treated = np.asarray(treated).ravel()
        self.T = len(self.treated)

        if isinstance(controls, dict):
            self.control_names = list(controls.keys())
            self.controls = np.column_stack([controls[k] for k in self.control_names])
        else:
            self.controls = np.asarray(controls)
            if self.controls.ndim == 1:
                self.controls = self.controls.reshape(-1, 1)

        if control_names is not None:
            self.control_names = control_names
        elif not hasattr(self, 'control_names'):
            self.control_names = [f'Control_{i}' for i in range(self.controls.shape[1])]

        self.treatment_time = treatment_time
        self.n_controls = self.controls.shape[1]

        # Split pre/post treatment
        self.pre_treated = self.treated[:treatment_time]
        self.post_treated = self.treated[treatment_time:]
        self.pre_controls = self.controls[:treatment_time, :]
        self.post_controls = self.controls[treatment_time:, :]

        self.weights = None
        self.synthetic = None

    def _optimize_weights(self) -> np.ndarray:
        """
        Find optimal weights to minimize pre-treatment RMSE.

        Solves: min ||Y_treated_pre - W * Y_controls_pre||²
        Subject to: w_i >= 0, sum(w) = 1
        """
        n_controls = self.pre_controls.shape[1]

        def objective(w):
            synthetic = self.pre_controls @ w
            return np.sum((self.pre_treated - synthetic)**2)

        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

        # Bounds: weights >= 0
        bounds = [(0, 1) for _ in range(n_controls)]

        # Initial guess: equal weights
        w0 = np.ones(n_controls) / n_controls

        # Optimize
        result = optimize.minimize(
            objective,
            w0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )

        return result.x

    def fit(self) -> np.ndarray:
        """
        Fit the synthetic control weights.

        Returns
        -------
        np.ndarray
            Optimal weights for each control unit
        """
        self.weights = self._optimize_weights()

        # Construct full synthetic control series
        self.synthetic = self.controls @ self.weights

        return self.weights

    def estimate_treatment_effect(
        self,
        run_placebo: bool = True,
        n_placebo: Optional[int] = None
    ) -> SyntheticControlResult:
        """
        Estimate treatment effect and conduct inference.

        Parameters
        ----------
        run_placebo : bool
            Whether to run placebo tests for inference
        n_placebo : int, optional
            Number of placebo tests (default: all controls)

        Returns
        -------
        SyntheticControlResult
        """
        if self.weights is None:
            self.fit()

        # Calculate effects
        synthetic_post = self.post_controls @ self.weights
        effects = self.post_treated - synthetic_post

        avg_effect = np.mean(effects)
        cumulative_effect = np.sum(effects)

        # Pre-treatment fit quality
        synthetic_pre = self.pre_controls @ self.weights
        pre_rmse = np.sqrt(np.mean((self.pre_treated - synthetic_pre)**2))

        if np.std(self.pre_treated) > 0 and np.std(synthetic_pre) > 0:
            pre_corr = np.corrcoef(self.pre_treated, synthetic_pre)[0, 1]
        else:
            pre_corr = 0.0

        # Placebo inference
        if run_placebo:
            p_value, ci = self._placebo_inference(n_placebo)
        else:
            p_value = np.nan
            ci = (np.nan, np.nan)

        # Format weights as dict
        weights_dict = {
            name: float(w)
            for name, w in zip(self.control_names, self.weights)
        }

        return SyntheticControlResult(
            treatment_effect=avg_effect,
            cumulative_effect=cumulative_effect,
            effects_by_period=effects.tolist(),
            weights=weights_dict,
            n_controls_used=int(np.sum(self.weights > 0.01)),
            pre_treatment_rmse=pre_rmse,
            pre_treatment_correlation=pre_corr,
            p_value=p_value,
            confidence_interval=ci,
            treatment_time=self.treatment_time,
            n_pre_periods=len(self.pre_treated),
            n_post_periods=len(self.post_treated)
        )

    def _placebo_inference(
        self,
        n_placebo: Optional[int] = None
    ) -> Tuple[float, Tuple[float, float]]:
        """
        Run placebo tests by applying synthetic control to each control unit.

        If the treatment effect for the treated unit is larger than
        most placebo effects, we have evidence of a real effect.
        """
        if n_placebo is None:
            n_placebo = self.n_controls

        # Calculate our treatment effect
        our_effect = np.mean(self.post_treated - self.post_controls @ self.weights)

        # Run placebo for each control unit
        placebo_effects = []

        for i in range(min(n_placebo, self.n_controls)):
            # Treat control i as if it were treated
            placebo_treated = self.controls[:, i]
            placebo_controls = np.delete(self.controls, i, axis=1)

            # Fit synthetic control
            pre_treated = placebo_treated[:self.treatment_time]
            pre_controls = placebo_controls[:self.treatment_time, :]
            post_treated = placebo_treated[self.treatment_time:]
            post_controls = placebo_controls[self.treatment_time:, :]

            # Optimize weights
            def objective(w):
                synthetic = pre_controls @ w
                return np.sum((pre_treated - synthetic)**2)

            n_c = pre_controls.shape[1]
            constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
            bounds = [(0, 1) for _ in range(n_c)]
            w0 = np.ones(n_c) / n_c

            try:
                result = optimize.minimize(
                    objective, w0,
                    method='SLSQP', bounds=bounds, constraints=constraints
                )
                weights = result.x

                # Calculate placebo effect
                synthetic_post = post_controls @ weights
                effect = np.mean(post_treated - synthetic_post)
                placebo_effects.append(effect)
            except:
                continue

        if len(placebo_effects) == 0:
            return np.nan, (np.nan, np.nan)

        placebo_effects = np.array(placebo_effects)

        # P-value: fraction of placebos with effect >= ours
        p_value = np.mean(np.abs(placebo_effects) >= np.abs(our_effect))

        # Confidence interval from placebo distribution
        ci = (
            np.percentile(placebo_effects, 2.5),
            np.percentile(placebo_effects, 97.5)
        )

        return p_value, ci

    def get_synthetic_series(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Return the treated and synthetic control time series.

        Returns
        -------
        treated : np.ndarray
        synthetic : np.ndarray
        """
        if self.synthetic is None:
            self.fit()

        return self.treated, self.synthetic

    def plot_data(self) -> Dict:
        """
        Return data for plotting.

        Returns dict with treated series, synthetic series, and treatment time.
        """
        if self.synthetic is None:
            self.fit()

        return {
            'time': list(range(self.T)),
            'treated': self.treated.tolist(),
            'synthetic': self.synthetic.tolist(),
            'treatment_time': self.treatment_time,
            'effects': (self.treated - self.synthetic).tolist()
        }


def construct_synthetic_control(
    treated: np.ndarray,
    controls: np.ndarray,
    treatment_time: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Quick function to construct synthetic control.

    Returns (weights, synthetic_series)
    """
    sc = SyntheticControlEstimator(treated, controls, treatment_time)
    weights = sc.fit()
    return weights, sc.synthetic


def estimate_treatment_effect_sc(
    treated: np.ndarray,
    controls: np.ndarray,
    treatment_time: int
) -> float:
    """
    Quick function to estimate treatment effect.

    Returns average post-treatment effect.
    """
    sc = SyntheticControlEstimator(treated, controls, treatment_time)
    result = sc.estimate_treatment_effect(run_placebo=False)
    return result.treatment_effect


if __name__ == "__main__":
    # Demo with synthetic data
    print("=" * 60)
    print("SYNTHETIC CONTROL METHOD DEMO")
    print("=" * 60)
    print()

    np.random.seed(42)

    # Time periods
    T = 50
    treatment_time = 30

    # Generate control units (5 similar regions)
    # They all follow a common trend + unit-specific effects
    common_trend = np.cumsum(np.random.normal(1, 0.5, T))

    controls = []
    control_names = ['Texas', 'Florida', 'Ohio', 'Georgia', 'Nevada']
    for name in control_names:
        unit_effect = np.random.normal(0, 2, T)
        series = 100 + common_trend + unit_effect
        controls.append(series)

    controls = np.column_stack(controls)

    # Generate treated unit (California)
    # Pre-treatment: follows similar pattern
    # Post-treatment: gets a boost of 15 units
    TRUE_EFFECT = 15
    california_pre = 100 + common_trend[:treatment_time] + np.random.normal(0, 2, treatment_time)

    # Mix the controls to approximate California pre-treatment
    # (True weights: 0.4 Texas + 0.3 Florida + 0.2 Ohio + 0.1 Georgia)
    true_weights = np.array([0.4, 0.3, 0.2, 0.1, 0.0])
    california_pre = controls[:treatment_time, :] @ true_weights + np.random.normal(0, 2, treatment_time)

    # Post-treatment: would have followed similar path, but got treatment effect
    california_counterfactual = controls[treatment_time:, :] @ true_weights
    california_post = california_counterfactual + TRUE_EFFECT + np.random.normal(0, 2, T - treatment_time)

    california = np.concatenate([california_pre, california_post])

    print(f"Simulating marketing campaign launch in California at t={treatment_time}")
    print(f"True treatment effect: {TRUE_EFFECT} units")
    print(f"Control regions: {control_names}")
    print()

    # Run synthetic control
    sc = SyntheticControlEstimator(
        california, controls, treatment_time, control_names
    )
    result = sc.estimate_treatment_effect()

    print(result)
    print()
    print(f"True effect: {TRUE_EFFECT}")
    print(f"SC estimate: {result.treatment_effect:.2f}")
    print(f"Estimation error: {abs(result.treatment_effect - TRUE_EFFECT):.2f}")
