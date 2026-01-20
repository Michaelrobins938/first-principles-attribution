"""
Instrumental Variables (IV) Estimation for Causal Attribution

Instrumental Variables provide causal estimates when there's unmeasured
confounding, by exploiting exogenous variation in treatment.

Key Idea:
- Find a variable Z (instrument) that:
  1. Affects treatment (relevance)
  2. Only affects outcome THROUGH treatment (exclusion restriction)
  3. Is independent of unmeasured confounders (exogeneity)

Examples in Marketing Attribution:
- Weather as instrument for store visits
- Ad server randomization as instrument for ad exposure
- Geographic distance as instrument for channel availability

Method: Two-Stage Least Squares (2SLS)
1. First stage: Regress Treatment on Instrument
2. Second stage: Regress Outcome on Predicted Treatment

Usage:
    iv = IVEstimator(instrument, treatment, outcome, covariates)
    result = iv.two_stage_least_squares()
    print(f"Causal effect: {result.coefficient:.3f}")
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class IVResult:
    """Results from instrumental variables estimation."""
    # Causal estimate
    coefficient: float  # 2SLS coefficient (causal effect)
    standard_error: float
    confidence_interval: Tuple[float, float]
    t_statistic: float
    p_value: float

    # First stage diagnostics
    first_stage_f: float  # F-statistic (should be > 10)
    first_stage_r2: float
    instrument_relevance: str  # 'strong', 'weak', 'invalid'

    # Sample info
    n_observations: int

    # OLS comparison
    ols_coefficient: float
    ols_se: float

    def __repr__(self):
        return f"""IVResult(
    2SLS Causal Effect: {self.coefficient:.4f}
    Standard Error:     {self.standard_error:.4f}
    95% CI:             [{self.confidence_interval[0]:.4f}, {self.confidence_interval[1]:.4f}]
    P-value:            {self.p_value:.4f}

    First Stage F-stat: {self.first_stage_f:.1f} ({self.instrument_relevance})
    First Stage R²:     {self.first_stage_r2:.3f}

    OLS Estimate:       {self.ols_coefficient:.4f} (biased if confounded)
    Difference:         {self.coefficient - self.ols_coefficient:+.4f}
)"""


class IVEstimator:
    """
    Two-Stage Least Squares (2SLS) estimator for causal effects.

    When treatment is endogenous (correlated with unobserved factors),
    IV/2SLS provides consistent causal estimates IF:

    1. RELEVANCE: Instrument predicts treatment (First stage F > 10)
    2. EXCLUSION: Instrument only affects outcome through treatment
    3. EXOGENEITY: Instrument is independent of unmeasured confounders

    Parameters
    ----------
    Z : np.ndarray
        Instrument(s) - shape (n,) or (n, k) for k instruments
    treatment : np.ndarray
        Endogenous treatment variable
    outcome : np.ndarray
        Outcome variable
    X : np.ndarray, optional
        Exogenous covariates (included in both stages)

    Example
    -------
    >>> # Instrument: Random ad server assignment
    >>> # Treatment: Whether user saw the ad
    >>> # Outcome: Whether user converted
    >>> iv = IVEstimator(
    ...     Z=ad_server_assignment,  # Random!
    ...     treatment=saw_ad,
    ...     outcome=converted
    ... )
    >>> result = iv.two_stage_least_squares()
    >>> print(f"Ad exposure CAUSES {result.coefficient:.1%} conversion lift")
    """

    def __init__(
        self,
        Z: np.ndarray,
        treatment: np.ndarray,
        outcome: np.ndarray,
        X: Optional[np.ndarray] = None
    ):
        self.Z = np.atleast_2d(np.asarray(Z).T).T
        if self.Z.ndim == 1:
            self.Z = self.Z.reshape(-1, 1)

        self.treatment = np.asarray(treatment).ravel()
        self.outcome = np.asarray(outcome).ravel()

        if X is not None:
            self.X = np.atleast_2d(np.asarray(X))
            if self.X.shape[0] != len(self.treatment):
                self.X = self.X.T
        else:
            self.X = None

        self.n = len(self.treatment)

    def two_stage_least_squares(self) -> IVResult:
        """
        Run 2SLS estimation.

        Stage 1: treatment = γ₀ + γ₁Z + γ₂X + v
        Stage 2: outcome = β₀ + β₁treatment_hat + β₂X + ε

        Returns
        -------
        IVResult
        """
        # Build design matrices
        if self.X is not None:
            W = np.column_stack([np.ones(self.n), self.Z, self.X])
            X_second = np.column_stack([np.ones(self.n), self.X])
        else:
            W = np.column_stack([np.ones(self.n), self.Z])
            X_second = np.ones((self.n, 1))

        # First stage: regress treatment on instruments + covariates
        gamma, resid_1, first_stage_stats = self._ols(W, self.treatment)
        treatment_hat = W @ gamma

        # First stage diagnostics
        first_stage_f = self._first_stage_f_test(W, self.treatment, gamma)
        first_stage_r2 = 1 - np.sum(resid_1**2) / np.sum(
            (self.treatment - self.treatment.mean())**2
        )

        # Instrument strength classification
        if first_stage_f > 10:
            relevance = 'strong'
        elif first_stage_f > 5:
            relevance = 'weak'
        else:
            relevance = 'invalid'

        # Second stage: regress outcome on predicted treatment + covariates
        if self.X is not None:
            Z_second = np.column_stack([np.ones(self.n), treatment_hat, self.X])
        else:
            Z_second = np.column_stack([np.ones(self.n), treatment_hat])

        beta, resid_2, _ = self._ols(Z_second, self.outcome)

        # The causal coefficient is β₁ (coefficient on treatment_hat)
        causal_coef = beta[1]

        # Standard error (corrected for 2SLS)
        # Use actual treatment, not predicted, for SE calculation
        if self.X is not None:
            Z_actual = np.column_stack([np.ones(self.n), self.treatment, self.X])
        else:
            Z_actual = np.column_stack([np.ones(self.n), self.treatment])

        resid_actual = self.outcome - Z_second @ beta
        sigma2 = np.sum(resid_actual**2) / (self.n - Z_second.shape[1])

        # Variance of beta using (Z'PZ)^-1 where P = W(W'W)^-1W'
        WtW_inv = np.linalg.inv(W.T @ W)
        P = W @ WtW_inv @ W.T
        ZtPZ = Z_actual.T @ P @ Z_actual

        try:
            var_beta = sigma2 * np.linalg.inv(ZtPZ)
            se = np.sqrt(var_beta[1, 1])
        except np.linalg.LinAlgError:
            se = np.nan

        # T-statistic and p-value
        if not np.isnan(se) and se > 0:
            t_stat = causal_coef / se
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), self.n - Z_second.shape[1]))
        else:
            t_stat = np.nan
            p_value = np.nan

        # Confidence interval
        t_crit = stats.t.ppf(0.975, self.n - Z_second.shape[1])
        ci = (causal_coef - t_crit * se, causal_coef + t_crit * se)

        # OLS comparison (biased)
        ols_beta, _, _ = self._ols(Z_actual, self.outcome)
        ols_coef = ols_beta[1]
        ols_resid = self.outcome - Z_actual @ ols_beta
        ols_sigma2 = np.sum(ols_resid**2) / (self.n - Z_actual.shape[1])
        try:
            ols_var = ols_sigma2 * np.linalg.inv(Z_actual.T @ Z_actual)
            ols_se = np.sqrt(ols_var[1, 1])
        except:
            ols_se = np.nan

        return IVResult(
            coefficient=causal_coef,
            standard_error=se,
            confidence_interval=ci,
            t_statistic=t_stat,
            p_value=p_value,
            first_stage_f=first_stage_f,
            first_stage_r2=first_stage_r2,
            instrument_relevance=relevance,
            n_observations=self.n,
            ols_coefficient=ols_coef,
            ols_se=ols_se
        )

    def _ols(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """Ordinary least squares regression."""
        try:
            XtX_inv = np.linalg.inv(X.T @ X)
            beta = XtX_inv @ X.T @ y
        except np.linalg.LinAlgError:
            # Use pseudo-inverse for singular matrices
            beta = np.linalg.pinv(X) @ y

        residuals = y - X @ beta
        stats_dict = {
            'rss': np.sum(residuals**2),
            'tss': np.sum((y - y.mean())**2)
        }

        return beta, residuals, stats_dict

    def _first_stage_f_test(
        self,
        W: np.ndarray,
        treatment: np.ndarray,
        gamma: np.ndarray
    ) -> float:
        """
        F-test for first stage relevance.

        Tests H0: all instrument coefficients = 0
        Rule of thumb: F > 10 indicates strong instruments
        """
        n = len(treatment)
        k_instruments = self.Z.shape[1]
        k_total = W.shape[1]

        # Full model residuals
        resid_full = treatment - W @ gamma

        # Restricted model (no instruments, only intercept + covariates)
        if self.X is not None:
            W_restricted = np.column_stack([np.ones(n), self.X])
        else:
            W_restricted = np.ones((n, 1))

        gamma_r, resid_r, _ = self._ols(W_restricted, treatment)

        # F-statistic
        rss_full = np.sum(resid_full**2)
        rss_restricted = np.sum(resid_r**2)

        numerator = (rss_restricted - rss_full) / k_instruments
        denominator = rss_full / (n - k_total)

        if denominator > 0:
            f_stat = numerator / denominator
        else:
            f_stat = 0

        return f_stat


def two_stage_least_squares(
    instrument: np.ndarray,
    treatment: np.ndarray,
    outcome: np.ndarray,
    covariates: Optional[np.ndarray] = None
) -> float:
    """
    Quick 2SLS estimation.

    Returns the causal coefficient.
    """
    iv = IVEstimator(instrument, treatment, outcome, covariates)
    result = iv.two_stage_least_squares()
    return result.coefficient


def check_instrument_validity(
    instrument: np.ndarray,
    treatment: np.ndarray,
    outcome: np.ndarray,
    covariates: Optional[np.ndarray] = None
) -> Dict[str, any]:
    """
    Check validity of an instrument.

    Returns diagnostics for the three IV assumptions:
    1. Relevance (testable)
    2. Exclusion (not directly testable)
    3. Exogeneity (not directly testable)

    Parameters
    ----------
    instrument : np.ndarray
    treatment : np.ndarray
    outcome : np.ndarray
    covariates : np.ndarray, optional

    Returns
    -------
    dict
        Validity diagnostics
    """
    iv = IVEstimator(instrument, treatment, outcome, covariates)
    result = iv.two_stage_least_squares()

    # Relevance check (testable)
    relevance_ok = result.first_stage_f > 10

    # Correlation checks
    z = np.asarray(instrument).ravel()
    corr_zt = np.corrcoef(z, treatment)[0, 1]
    corr_zy = np.corrcoef(z, outcome)[0, 1]

    # Indirect effect ratio (if instrument affects outcome only through treatment)
    # we expect corr(Z,Y) ≈ corr(Z,T) * causal_effect
    expected_corr_zy = corr_zt * result.coefficient
    exclusion_ratio = corr_zy / expected_corr_zy if expected_corr_zy != 0 else np.nan

    return {
        'relevance': {
            'first_stage_f': result.first_stage_f,
            'is_strong': relevance_ok,
            'correlation_z_treatment': corr_zt,
            'first_stage_r2': result.first_stage_r2
        },
        'exclusion': {
            'correlation_z_outcome': corr_zy,
            'expected_if_valid': expected_corr_zy,
            'ratio': exclusion_ratio,
            'note': 'Ratio near 1.0 supports exclusion restriction (not definitive)'
        },
        'exogeneity': {
            'note': 'Cannot be tested directly. Requires domain knowledge.',
            'recommendation': 'Verify instrument is as-if random or natural experiment'
        },
        'causal_estimate': result.coefficient,
        'ols_estimate': result.ols_coefficient,
        'endogeneity_bias': result.ols_coefficient - result.coefficient
    }


if __name__ == "__main__":
    # Demo with synthetic data
    print("=" * 60)
    print("INSTRUMENTAL VARIABLES DEMO")
    print("=" * 60)
    print()

    np.random.seed(42)
    n = 2000

    # Unobserved confounder (affects both treatment and outcome)
    U = np.random.normal(0, 1, n)

    # Instrument (exogenous - random ad server assignment)
    Z = np.random.binomial(1, 0.5, n)

    # Treatment depends on instrument AND confounder
    treatment_logit = -0.5 + 1.5 * Z + 0.8 * U
    treatment = (np.random.random(n) < 1 / (1 + np.exp(-treatment_logit))).astype(float)

    # Outcome depends on treatment AND confounder
    # True causal effect = 0.3
    TRUE_EFFECT = 0.3
    outcome_logit = -1 + TRUE_EFFECT * treatment + 0.6 * U
    outcome = (np.random.random(n) < 1 / (1 + np.exp(-outcome_logit))).astype(float)

    print(f"True causal effect: {TRUE_EFFECT}")
    print(f"Instrument (Z) is random: mean = {Z.mean():.2f}")
    print()

    # Run IV estimation
    iv = IVEstimator(Z, treatment, outcome)
    result = iv.two_stage_least_squares()

    print(result)
    print()

    # Check instrument validity
    print("Instrument Validity Check:")
    print("-" * 40)
    validity = check_instrument_validity(Z, treatment, outcome)
    print(f"First stage F: {validity['relevance']['first_stage_f']:.1f} "
          f"({'Strong' if validity['relevance']['is_strong'] else 'WEAK'})")
    print(f"Corr(Z, Treatment): {validity['relevance']['correlation_z_treatment']:.3f}")
    print(f"Estimated bias in OLS: {validity['endogeneity_bias']:.4f}")
