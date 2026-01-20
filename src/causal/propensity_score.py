"""
Propensity Score Matching for Causal Attribution

When A/B tests aren't available, propensity score matching (PSM) provides
QUASI-EXPERIMENTAL control by matching treated and untreated users
with similar characteristics.

Key Idea:
- Users who were exposed to a channel aren't random
- They differ systematically from non-exposed users
- PSM matches on predicted probability of exposure
- This reduces (but doesn't eliminate) selection bias

Requirements:
- Rich user features (demographics, behavior, intent signals)
- Overlap: Both treated and untreated users at each propensity level
- No unmeasured confounders (strong assumption!)

Usage:
    psm = PropensityScoreEstimator(features, treatment, outcome)
    ate = psm.estimate_average_treatment_effect()
    print(f"Estimated causal effect: {ate:.3f}")
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PSMResult:
    """Results from propensity score matching analysis."""
    # Causal estimates
    ate: float  # Average Treatment Effect
    att: float  # Average Treatment Effect on Treated
    atc: float  # Average Treatment Effect on Control

    # Confidence intervals
    ate_ci: Tuple[float, float]
    ate_se: float

    # Matching quality
    n_matched: int
    n_unmatched: int
    balance_improvement: float  # Standardized mean difference reduction

    # Diagnostics
    common_support_fraction: float
    propensity_overlap: float

    def __repr__(self):
        return f"""PSMResult(
    Average Treatment Effect (ATE): {self.ate:.4f}
    95% CI: [{self.ate_ci[0]:.4f}, {self.ate_ci[1]:.4f}]
    Standard Error: {self.ate_se:.4f}

    Matched pairs: {self.n_matched}
    Balance improvement: {self.balance_improvement:.1%}
    Common support: {self.common_support_fraction:.1%}
)"""


class PropensityScoreEstimator:
    """
    Estimate causal effects using propensity score matching.

    The propensity score is P(Treatment | X) - the probability of
    receiving treatment given observed features X.

    Matching on propensity scores approximates randomization:
    within matched pairs, treatment is "as if" random.

    Parameters
    ----------
    X : np.ndarray
        Feature matrix (n_samples, n_features)
    treatment : np.ndarray
        Binary treatment indicator (1=treated, 0=control)
    outcome : np.ndarray
        Outcome variable (e.g., conversion, revenue)
    caliper : float
        Maximum propensity score distance for matching (default: 0.1)

    Example
    -------
    >>> # Estimate causal effect of Email exposure
    >>> psm = PropensityScoreEstimator(
    ...     X=user_features,        # Demographics, behavior
    ...     treatment=saw_email,    # 1 if user saw email, 0 otherwise
    ...     outcome=converted       # 1 if converted, 0 otherwise
    ... )
    >>> result = psm.estimate_average_treatment_effect()
    >>> print(f"Email CAUSES {result.ate:.1%} increase in conversion")
    """

    def __init__(
        self,
        X: np.ndarray,
        treatment: np.ndarray,
        outcome: np.ndarray,
        caliper: float = 0.1
    ):
        self.X = np.asarray(X)
        self.treatment = np.asarray(treatment).astype(int)
        self.outcome = np.asarray(outcome).astype(float)
        self.caliper = caliper

        self.propensity_scores = None
        self.matched_pairs = None

    def fit_propensity_model(self) -> np.ndarray:
        """
        Estimate propensity scores using logistic regression.

        Returns array of P(Treatment=1 | X) for each observation.
        """
        # Simple logistic regression implementation
        # In production, use sklearn.linear_model.LogisticRegression

        n, p = self.X.shape

        # Add intercept
        X_aug = np.column_stack([np.ones(n), self.X])

        # Initialize coefficients
        beta = np.zeros(p + 1)

        # Newton-Raphson optimization
        for _ in range(50):
            # Predicted probabilities
            z = X_aug @ beta
            z = np.clip(z, -20, 20)  # Numerical stability
            probs = 1 / (1 + np.exp(-z))

            # Gradient
            grad = X_aug.T @ (self.treatment - probs)

            # Hessian
            W = np.diag(probs * (1 - probs))
            hess = -X_aug.T @ W @ X_aug

            # Update (with regularization for stability)
            try:
                hess_inv = np.linalg.inv(hess - 0.01 * np.eye(p + 1))
                beta = beta - hess_inv @ grad
            except np.linalg.LinAlgError:
                break

        # Final predictions
        z = X_aug @ beta
        z = np.clip(z, -20, 20)
        self.propensity_scores = 1 / (1 + np.exp(-z))

        return self.propensity_scores

    def match(self, method: str = 'nearest') -> List[Tuple[int, int]]:
        """
        Match treated and control units based on propensity scores.

        Parameters
        ----------
        method : str
            'nearest' for nearest neighbor matching
            'caliper' for caliper matching (with distance threshold)

        Returns
        -------
        list
            List of (treated_idx, control_idx) pairs
        """
        if self.propensity_scores is None:
            self.fit_propensity_model()

        treated_idx = np.where(self.treatment == 1)[0]
        control_idx = np.where(self.treatment == 0)[0]

        ps_treated = self.propensity_scores[treated_idx]
        ps_control = self.propensity_scores[control_idx]

        matched_pairs = []
        used_controls = set()

        for t_i, t_idx in enumerate(treated_idx):
            t_ps = ps_treated[t_i]

            # Find closest control not yet used
            best_dist = float('inf')
            best_c_idx = None

            for c_i, c_idx in enumerate(control_idx):
                if c_idx in used_controls:
                    continue

                dist = abs(t_ps - ps_control[c_i])

                if dist < best_dist:
                    best_dist = dist
                    best_c_idx = c_idx

            # Apply caliper
            if best_c_idx is not None and best_dist <= self.caliper:
                matched_pairs.append((t_idx, best_c_idx))
                used_controls.add(best_c_idx)

        self.matched_pairs = matched_pairs
        return matched_pairs

    def estimate_average_treatment_effect(self) -> PSMResult:
        """
        Estimate ATE using matched pairs.

        The ATE is the average difference in outcomes between
        treated and matched control units.
        """
        if self.matched_pairs is None:
            self.match()

        if len(self.matched_pairs) == 0:
            raise ValueError("No matched pairs found. Check caliper or data.")

        # Calculate treatment effects for matched pairs
        effects = []
        for t_idx, c_idx in self.matched_pairs:
            effect = self.outcome[t_idx] - self.outcome[c_idx]
            effects.append(effect)

        effects = np.array(effects)

        # ATE estimate
        ate = np.mean(effects)

        # Standard error (clustered by pair)
        ate_se = np.std(effects, ddof=1) / np.sqrt(len(effects))

        # Confidence interval
        t_crit = stats.t.ppf(0.975, len(effects) - 1)
        ate_ci = (ate - t_crit * ate_se, ate + t_crit * ate_se)

        # ATT and ATC
        att = ate  # For PSM, ATT ≈ ATE on matched sample
        atc = ate  # Symmetric matching

        # Balance diagnostics
        balance_improvement = self._calculate_balance_improvement()

        # Common support
        cs_frac = len(self.matched_pairs) / sum(self.treatment)

        # Propensity overlap
        ps_treated = self.propensity_scores[self.treatment == 1]
        ps_control = self.propensity_scores[self.treatment == 0]
        overlap = self._calculate_overlap(ps_treated, ps_control)

        return PSMResult(
            ate=ate,
            att=att,
            atc=atc,
            ate_ci=ate_ci,
            ate_se=ate_se,
            n_matched=len(self.matched_pairs),
            n_unmatched=sum(self.treatment) - len(self.matched_pairs),
            balance_improvement=balance_improvement,
            common_support_fraction=cs_frac,
            propensity_overlap=overlap
        )

    def _calculate_balance_improvement(self) -> float:
        """Calculate standardized mean difference reduction after matching."""
        if self.matched_pairs is None or len(self.matched_pairs) == 0:
            return 0.0

        # Pre-matching balance
        treated_mask = self.treatment == 1
        smd_before = []

        for j in range(self.X.shape[1]):
            mean_t = np.mean(self.X[treated_mask, j])
            mean_c = np.mean(self.X[~treated_mask, j])
            std_pooled = np.sqrt(
                (np.var(self.X[treated_mask, j]) +
                 np.var(self.X[~treated_mask, j])) / 2
            )
            if std_pooled > 0:
                smd_before.append(abs(mean_t - mean_c) / std_pooled)

        # Post-matching balance
        matched_t = np.array([p[0] for p in self.matched_pairs])
        matched_c = np.array([p[1] for p in self.matched_pairs])
        smd_after = []

        for j in range(self.X.shape[1]):
            mean_t = np.mean(self.X[matched_t, j])
            mean_c = np.mean(self.X[matched_c, j])
            std_pooled = np.sqrt(
                (np.var(self.X[matched_t, j]) +
                 np.var(self.X[matched_c, j])) / 2
            )
            if std_pooled > 0:
                smd_after.append(abs(mean_t - mean_c) / std_pooled)

        if len(smd_before) == 0:
            return 0.0

        avg_before = np.mean(smd_before)
        avg_after = np.mean(smd_after) if smd_after else 0

        if avg_before == 0:
            return 0.0

        return (avg_before - avg_after) / avg_before

    def _calculate_overlap(
        self,
        ps_treated: np.ndarray,
        ps_control: np.ndarray
    ) -> float:
        """Calculate propensity score distribution overlap."""
        # Range overlap
        t_min, t_max = ps_treated.min(), ps_treated.max()
        c_min, c_max = ps_control.min(), ps_control.max()

        overlap_min = max(t_min, c_min)
        overlap_max = min(t_max, c_max)

        if overlap_max <= overlap_min:
            return 0.0

        # Fraction in overlap region
        t_in_overlap = np.mean((ps_treated >= overlap_min) &
                               (ps_treated <= overlap_max))
        c_in_overlap = np.mean((ps_control >= overlap_min) &
                               (ps_control <= overlap_max))

        return (t_in_overlap + c_in_overlap) / 2


def calculate_propensity_scores(
    X: np.ndarray,
    treatment: np.ndarray
) -> np.ndarray:
    """
    Quick function to calculate propensity scores.

    Parameters
    ----------
    X : np.ndarray
        Feature matrix
    treatment : np.ndarray
        Treatment indicator

    Returns
    -------
    np.ndarray
        Propensity scores
    """
    psm = PropensityScoreEstimator(X, treatment, np.zeros(len(treatment)))
    return psm.fit_propensity_model()


def match_propensity_scores(
    propensity_scores: np.ndarray,
    treatment: np.ndarray,
    caliper: float = 0.1
) -> List[Tuple[int, int]]:
    """
    Match treated and control units by propensity score.

    Parameters
    ----------
    propensity_scores : np.ndarray
        Pre-computed propensity scores
    treatment : np.ndarray
        Treatment indicator
    caliper : float
        Maximum distance for matching

    Returns
    -------
    list
        Matched pairs (treated_idx, control_idx)
    """
    psm = PropensityScoreEstimator(
        np.zeros((len(treatment), 1)),
        treatment,
        np.zeros(len(treatment)),
        caliper=caliper
    )
    psm.propensity_scores = propensity_scores
    return psm.match()


def estimate_ate_psm(
    X: np.ndarray,
    treatment: np.ndarray,
    outcome: np.ndarray,
    caliper: float = 0.1
) -> float:
    """
    Quick function to estimate ATE using PSM.

    Parameters
    ----------
    X : np.ndarray
        Feature matrix
    treatment : np.ndarray
        Treatment indicator
    outcome : np.ndarray
        Outcome variable
    caliper : float
        Matching caliper

    Returns
    -------
    float
        Estimated Average Treatment Effect
    """
    psm = PropensityScoreEstimator(X, treatment, outcome, caliper)
    result = psm.estimate_average_treatment_effect()
    return result.ate


if __name__ == "__main__":
    # Demo with synthetic data
    print("=" * 60)
    print("PROPENSITY SCORE MATCHING DEMO")
    print("=" * 60)
    print()

    np.random.seed(42)
    n = 2000

    # Generate confounders
    age = np.random.normal(35, 10, n)
    income = np.random.normal(50000, 20000, n)
    engagement = np.random.normal(0.5, 0.2, n)

    X = np.column_stack([
        (age - 35) / 10,
        (income - 50000) / 20000,
        (engagement - 0.5) / 0.2
    ])

    # Treatment probability depends on confounders
    # (high engagement users more likely to see emails)
    logit = -1 + 0.3 * X[:, 0] + 0.5 * X[:, 1] + 1.2 * X[:, 2]
    p_treat = 1 / (1 + np.exp(-logit))
    treatment = (np.random.random(n) < p_treat).astype(int)

    # Outcome depends on confounders AND treatment
    # True causal effect = 0.15
    TRUE_EFFECT = 0.15
    outcome_logit = -2 + 0.2 * X[:, 0] + 0.3 * X[:, 1] + 0.8 * X[:, 2]
    outcome_logit += TRUE_EFFECT * treatment
    outcome = (np.random.random(n) < 1 / (1 + np.exp(-outcome_logit))).astype(int)

    print(f"True causal effect: {TRUE_EFFECT}")
    print(f"Treatment rate: {treatment.mean():.1%}")
    print(f"Outcome rate: {outcome.mean():.1%}")
    print()

    # Naive comparison (biased)
    naive = outcome[treatment == 1].mean() - outcome[treatment == 0].mean()
    print(f"Naive estimate (biased): {naive:.4f}")

    # PSM estimate
    psm = PropensityScoreEstimator(X, treatment, outcome, caliper=0.2)
    result = psm.estimate_average_treatment_effect()

    print()
    print(result)
    print()
    print(f"True effect: {TRUE_EFFECT:.4f}")
    print(f"PSM estimate: {result.ate:.4f}")
    print(f"Bias reduction: {abs(naive - TRUE_EFFECT) - abs(result.ate - TRUE_EFFECT):.4f}")
