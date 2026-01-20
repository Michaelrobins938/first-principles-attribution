"""
Causal Inference Module for First-Principles Attribution

Moves from CONTRIBUTION (what the Markov-Shapley model provides)
to CAUSATION (true causal effects).

Methods implemented:
- A/B Test Analysis: Gold standard with randomized experiments
- Propensity Score Matching: Quasi-experimental control
- Instrumental Variables: Exogenous variation estimation
- Regression Discontinuity: Local causal effects at thresholds
- Synthetic Control: Counterfactual comparison

Each method has different data requirements and assumptions.
See individual module docstrings for details.
"""

from .ab_test import (
    ABTestAnalyzer,
    calculate_lift,
    calculate_statistical_significance,
    run_ab_test_analysis
)

from .propensity_score import (
    PropensityScoreEstimator,
    calculate_propensity_scores,
    match_propensity_scores,
    estimate_ate_psm
)

from .instrumental_variables import (
    IVEstimator,
    two_stage_least_squares,
    check_instrument_validity
)

from .regression_discontinuity import (
    RDDEstimator,
    estimate_local_average_treatment_effect,
    plot_discontinuity
)

from .synthetic_control import (
    SyntheticControlEstimator,
    construct_synthetic_control,
    estimate_treatment_effect_sc
)

__all__ = [
    # A/B Testing
    'ABTestAnalyzer',
    'calculate_lift',
    'calculate_statistical_significance',
    'run_ab_test_analysis',

    # Propensity Score Matching
    'PropensityScoreEstimator',
    'calculate_propensity_scores',
    'match_propensity_scores',
    'estimate_ate_psm',

    # Instrumental Variables
    'IVEstimator',
    'two_stage_least_squares',
    'check_instrument_validity',

    # Regression Discontinuity
    'RDDEstimator',
    'estimate_local_average_treatment_effect',
    'plot_discontinuity',

    # Synthetic Control
    'SyntheticControlEstimator',
    'construct_synthetic_control',
    'estimate_treatment_effect_sc'
]
