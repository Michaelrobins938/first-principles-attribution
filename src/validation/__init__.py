"""
Validation and Weight Learning Module

Provides tools for:
- Comparing model output to ground truth
- Learning context weights from data
- Validating against heuristic baselines
"""

from .validation_suite import (
    compare_to_ground_truth,
    compare_against_baselines,
    generate_synthetic_ground_truth,
    run_validation_report,
    ValidationResult
)

from .weight_learning import (
    tune_weights_cv,
    tune_weights_mle,
    save_learned_weights,
    load_learned_weights,
    LearningResult,
    DEFAULT_CONTEXT_WEIGHTS
)

__all__ = [
    'compare_to_ground_truth',
    'compare_against_baselines',
    'generate_synthetic_ground_truth',
    'run_validation_report',
    'ValidationResult',
    'tune_weights_cv',
    'tune_weights_mle',
    'save_learned_weights',
    'load_learned_weights',
    'LearningResult',
    'DEFAULT_CONTEXT_WEIGHTS'
]
