"""
Regression Discontinuity Design (RDD) for Causal Attribution

RDD estimates LOCAL CAUSAL EFFECTS at a threshold/cutoff point.

Key Idea:
- Treatment is determined by whether a running variable X crosses a threshold c
- Units just above and just below c are nearly identical
- Any jump in outcome at c is attributable to treatment

Examples in Marketing:
- Loyalty tier thresholds (spend $1000 → Gold status)
- Free shipping thresholds (order $50 → free shipping)
- Retargeting frequency caps (seen ad 5+ times → no more ads)

Requirements:
- Sharp discontinuity in treatment at threshold
- Running variable cannot be precisely manipulated
- Continuity of potential outcomes at threshold

Usage:
    rdd = RDDEstimator(running_var, outcome, cutoff=100)
    result = rdd.estimate_treatment_effect()
    print(f"Treatment effect at cutoff: {result.late:.3f}")
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class RDDResult:
    """Results from regression discontinuity estimation."""
    # Causal estimate
    late: float  # Local Average Treatment Effect at cutoff
    standard_error: float
    confidence_interval: Tuple[float, float]
    t_statistic: float
    p_value: float

    # Design parameters
    cutoff: float
    bandwidth: float
    n_treated: int
    n_control: int

    # Diagnostics
    left_mean: float  # Mean outcome just below cutoff
    right_mean: float  # Mean outcome just above cutoff
    mccrary_p: float  # McCrary density test p-value (manipulation check)

    def __repr__(self):
        return f"""RDDResult(
    Local Average Treatment Effect: {self.late:.4f}
    Standard Error:                 {self.standard_error:.4f}
    95% CI:                         [{self.confidence_interval[0]:.4f}, {self.confidence_interval[1]:.4f}]
    P-value:                        {self.p_value:.4f}

    Cutoff:      {self.cutoff}
    Bandwidth:   {self.bandwidth:.2f}
    N (treated): {self.n_treated}
    N (control): {self.n_control}

    Mean below cutoff:  {self.left_mean:.4f}
    Mean above cutoff:  {self.right_mean:.4f}
    Jump at cutoff:     {self.right_mean - self.left_mean:.4f}

    McCrary test p-value: {self.mccrary_p:.3f} {'(OK)' if self.mccrary_p > 0.05 else '(MANIPULATION?)'}
)"""


class RDDEstimator:
    """
    Regression Discontinuity Design estimator.

    Estimates the causal effect of treatment at a sharp threshold.

    Parameters
    ----------
    running_var : np.ndarray
        The running/forcing variable that determines treatment
    outcome : np.ndarray
        Outcome variable
    cutoff : float
        Threshold value where treatment changes
    bandwidth : float, optional
        Window around cutoff (default: automatic selection)

    Example
    -------
    >>> # Effect of Gold loyalty status (threshold: $1000 spend)
    >>> rdd = RDDEstimator(
    ...     running_var=customer_spend,
    ...     outcome=next_year_spend,
    ...     cutoff=1000
    ... )
    >>> result = rdd.estimate_treatment_effect()
    >>> print(f"Gold status CAUSES ${result.late:.0f} increase in spend")
    """

    def __init__(
        self,
        running_var: np.ndarray,
        outcome: np.ndarray,
        cutoff: float,
        bandwidth: Optional[float] = None
    ):
        self.X = np.asarray(running_var).ravel()
        self.Y = np.asarray(outcome).ravel()
        self.cutoff = cutoff

        # Automatic bandwidth selection (IK method simplified)
        if bandwidth is None:
            self.bandwidth = self._optimal_bandwidth()
        else:
            self.bandwidth = bandwidth

    def _optimal_bandwidth(self) -> float:
        """
        Select optimal bandwidth using simplified IK method.

        Uses rule of thumb: h ≈ 1.06 * σ * n^(-1/5) scaled by data range
        """
        sigma = np.std(self.X)
        n = len(self.X)
        h_rot = 1.06 * sigma * (n ** (-1/5))

        # Scale to reasonable fraction of data range
        data_range = self.X.max() - self.X.min()
        h = min(h_rot, data_range * 0.25)

        return max(h, data_range * 0.05)  # At least 5% of range

    def estimate_treatment_effect(
        self,
        polynomial_order: int = 1,
        kernel: str = 'triangular'
    ) -> RDDResult:
        """
        Estimate LATE using local polynomial regression.

        Parameters
        ----------
        polynomial_order : int
            Order of polynomial (1 = linear, 2 = quadratic)
        kernel : str
            Kernel for weighting ('triangular', 'uniform', 'epanechnikov')

        Returns
        -------
        RDDResult
        """
        # Center running variable at cutoff
        X_centered = self.X - self.cutoff

        # Treatment indicator
        D = (self.X >= self.cutoff).astype(float)

        # Select observations within bandwidth
        in_bandwidth = np.abs(X_centered) <= self.bandwidth
        X_bw = X_centered[in_bandwidth]
        Y_bw = self.Y[in_bandwidth]
        D_bw = D[in_bandwidth]

        n_treated = np.sum(D_bw)
        n_control = np.sum(1 - D_bw)

        if n_treated < 10 or n_control < 10:
            raise ValueError(
                f"Insufficient observations near cutoff. "
                f"Treated: {n_treated}, Control: {n_control}. "
                f"Try increasing bandwidth."
            )

        # Compute kernel weights
        weights = self._kernel_weights(X_bw, kernel)

        # Build design matrix for local polynomial
        if polynomial_order == 1:
            # Y = β₀ + β₁D + β₂X + β₃(D*X) + ε
            design = np.column_stack([
                np.ones(len(X_bw)),
                D_bw,
                X_bw,
                D_bw * X_bw
            ])
        elif polynomial_order == 2:
            design = np.column_stack([
                np.ones(len(X_bw)),
                D_bw,
                X_bw,
                D_bw * X_bw,
                X_bw**2,
                D_bw * X_bw**2
            ])
        else:
            raise ValueError("polynomial_order must be 1 or 2")

        # Weighted least squares
        W = np.diag(weights)
        try:
            XtWX_inv = np.linalg.inv(design.T @ W @ design)
            beta = XtWX_inv @ design.T @ W @ Y_bw
        except np.linalg.LinAlgError:
            beta = np.linalg.pinv(design.T @ W @ design) @ design.T @ W @ Y_bw
            XtWX_inv = np.linalg.pinv(design.T @ W @ design)

        # Treatment effect is coefficient on D (β₁)
        late = beta[1]

        # Standard error
        residuals = Y_bw - design @ beta
        sigma2 = np.sum(weights * residuals**2) / (np.sum(weights) - len(beta))
        var_beta = sigma2 * XtWX_inv
        se = np.sqrt(var_beta[1, 1])

        # T-statistic and p-value
        df = np.sum(in_bandwidth) - len(beta)
        t_stat = late / se if se > 0 else 0
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))

        # Confidence interval
        t_crit = stats.t.ppf(0.975, df)
        ci = (late - t_crit * se, late + t_crit * se)

        # Diagnostics
        left_mean = np.mean(Y_bw[D_bw == 0])
        right_mean = np.mean(Y_bw[D_bw == 1])

        # McCrary manipulation test (simplified)
        mccrary_p = self._mccrary_test()

        return RDDResult(
            late=late,
            standard_error=se,
            confidence_interval=ci,
            t_statistic=t_stat,
            p_value=p_value,
            cutoff=self.cutoff,
            bandwidth=self.bandwidth,
            n_treated=int(n_treated),
            n_control=int(n_control),
            left_mean=left_mean,
            right_mean=right_mean,
            mccrary_p=mccrary_p
        )

    def _kernel_weights(
        self,
        X_centered: np.ndarray,
        kernel: str
    ) -> np.ndarray:
        """Compute kernel weights for observations."""
        u = X_centered / self.bandwidth

        if kernel == 'uniform':
            weights = np.ones(len(u))
        elif kernel == 'triangular':
            weights = np.maximum(0, 1 - np.abs(u))
        elif kernel == 'epanechnikov':
            weights = np.maximum(0, 0.75 * (1 - u**2))
        else:
            raise ValueError(f"Unknown kernel: {kernel}")

        return weights

    def _mccrary_test(self) -> float:
        """
        Simplified McCrary density test for manipulation.

        Tests if there's a discontinuity in the density of the running
        variable at the cutoff (which would suggest manipulation).

        Returns p-value. p < 0.05 suggests potential manipulation.
        """
        # Count observations in bins on each side of cutoff
        n_bins = 20
        bin_width = self.bandwidth / n_bins

        left_counts = []
        right_counts = []

        for i in range(n_bins):
            left_lower = self.cutoff - (i + 1) * bin_width
            left_upper = self.cutoff - i * bin_width
            left_counts.append(np.sum((self.X >= left_lower) & (self.X < left_upper)))

            right_lower = self.cutoff + i * bin_width
            right_upper = self.cutoff + (i + 1) * bin_width
            right_counts.append(np.sum((self.X >= right_lower) & (self.X < right_upper)))

        # Compare densities near cutoff
        near_left = sum(left_counts[:3])
        near_right = sum(right_counts[:3])

        # Simple chi-square test for density discontinuity
        expected = (near_left + near_right) / 2
        if expected > 0:
            chi2 = (near_left - expected)**2 / expected + (near_right - expected)**2 / expected
            p_value = 1 - stats.chi2.cdf(chi2, 1)
        else:
            p_value = 1.0

        return p_value

    def plot_data(self) -> Dict:
        """
        Return data for plotting the RDD.

        Returns dict with:
        - scatter_x, scatter_y: raw data points
        - fit_left_x, fit_left_y: fitted line below cutoff
        - fit_right_x, fit_right_y: fitted line above cutoff
        """
        # Fit separate lines on each side
        left_mask = self.X < self.cutoff
        right_mask = self.X >= self.cutoff

        X_left = self.X[left_mask]
        Y_left = self.Y[left_mask]
        X_right = self.X[right_mask]
        Y_right = self.Y[right_mask]

        # Linear fits
        if len(X_left) > 1:
            coef_left = np.polyfit(X_left, Y_left, 1)
            fit_left_x = np.linspace(X_left.min(), self.cutoff, 50)
            fit_left_y = np.polyval(coef_left, fit_left_x)
        else:
            fit_left_x = fit_left_y = []

        if len(X_right) > 1:
            coef_right = np.polyfit(X_right, Y_right, 1)
            fit_right_x = np.linspace(self.cutoff, X_right.max(), 50)
            fit_right_y = np.polyval(coef_right, fit_right_x)
        else:
            fit_right_x = fit_right_y = []

        return {
            'scatter_x': self.X.tolist(),
            'scatter_y': self.Y.tolist(),
            'fit_left_x': list(fit_left_x),
            'fit_left_y': list(fit_left_y),
            'fit_right_x': list(fit_right_x),
            'fit_right_y': list(fit_right_y),
            'cutoff': self.cutoff
        }


def estimate_local_average_treatment_effect(
    running_var: np.ndarray,
    outcome: np.ndarray,
    cutoff: float,
    bandwidth: Optional[float] = None
) -> float:
    """
    Quick function to estimate LATE at a cutoff.

    Returns the treatment effect.
    """
    rdd = RDDEstimator(running_var, outcome, cutoff, bandwidth)
    result = rdd.estimate_treatment_effect()
    return result.late


def plot_discontinuity(
    running_var: np.ndarray,
    outcome: np.ndarray,
    cutoff: float,
    n_bins: int = 20
) -> Dict:
    """
    Create binned scatter plot data for RDD visualization.

    Returns dict with bin centers, means, and fit lines.
    """
    X = np.asarray(running_var)
    Y = np.asarray(outcome)

    # Create bins
    x_min, x_max = X.min(), X.max()
    bins = np.linspace(x_min, x_max, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    # Calculate bin means
    bin_means = []
    bin_counts = []
    for i in range(n_bins):
        mask = (X >= bins[i]) & (X < bins[i + 1])
        if mask.sum() > 0:
            bin_means.append(np.mean(Y[mask]))
            bin_counts.append(mask.sum())
        else:
            bin_means.append(np.nan)
            bin_counts.append(0)

    return {
        'bin_centers': bin_centers.tolist(),
        'bin_means': bin_means,
        'bin_counts': bin_counts,
        'cutoff': cutoff,
        'raw_x': X.tolist(),
        'raw_y': Y.tolist()
    }


if __name__ == "__main__":
    # Demo with synthetic data
    print("=" * 60)
    print("REGRESSION DISCONTINUITY DEMO")
    print("=" * 60)
    print()

    np.random.seed(42)
    n = 1000

    # Running variable: customer spend
    X = np.random.uniform(500, 1500, n)

    # Treatment: Gold status if spend >= 1000
    cutoff = 1000
    D = (X >= cutoff).astype(float)

    # Outcome: next year spend
    # Baseline relationship + treatment effect of $200
    TRUE_EFFECT = 200
    noise = np.random.normal(0, 100, n)

    # Smooth relationship with treatment jump
    Y = 500 + 0.3 * X + TRUE_EFFECT * D + noise

    print(f"Simulating loyalty program threshold at ${cutoff}")
    print(f"True treatment effect (Gold status): ${TRUE_EFFECT}")
    print()

    # Run RDD
    rdd = RDDEstimator(X, Y, cutoff)
    result = rdd.estimate_treatment_effect()

    print(result)
    print()
    print(f"True effect: ${TRUE_EFFECT}")
    print(f"RDD estimate: ${result.late:.0f}")
    print(f"Estimation error: ${abs(result.late - TRUE_EFFECT):.0f}")
