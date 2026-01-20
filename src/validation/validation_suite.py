"""
Validation Suite for First-Principles Attribution Engine

Compares model attribution outputs against ground truth datasets
to measure accuracy and provide empirical validation.

IMPORTANT: This validates CONTRIBUTION measurement, not CAUSATION.
See WHITEPAPER.md section "Limitations and Causal Interpretation" for details.
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Results from comparing model output to ground truth."""
    rank_correlation: float      # Spearman rho (-1 to 1)
    magnitude_error: float       # Mean Absolute Percentage Error
    top_channel_match: bool      # Did we pick the same winner?
    top_k_overlap: float         # Fraction of top-k channels matching
    confidence_calibration: float  # How well do CIs match empirical error?

    def __repr__(self):
        return f"""ValidationResult(
    rank_correlation={self.rank_correlation:.3f},
    magnitude_error={self.magnitude_error:.1%},
    top_channel_match={self.top_channel_match},
    top_k_overlap={self.top_k_overlap:.1%},
    confidence_calibration={self.confidence_calibration:.3f}
)"""


def compare_to_ground_truth(
    model_output: Dict[str, float],
    true_effects: Dict[str, float],
    model_confidence_intervals: Optional[Dict[str, Tuple[float, float]]] = None
) -> ValidationResult:
    """
    Compare model attribution to known causal effects.

    Parameters
    ----------
    model_output : dict
        Channel -> attribution value from the model
    true_effects : dict
        Channel -> true causal effect (from A/B test or simulation)
    model_confidence_intervals : dict, optional
        Channel -> (lower, upper) 90% CI bounds

    Returns
    -------
    ValidationResult
        Comprehensive comparison metrics

    Example
    -------
    >>> model = {'Search': 0.42, 'Email': 0.25, 'Direct': 0.18}
    >>> truth = {'Search': 0.38, 'Email': 0.30, 'Direct': 0.20}
    >>> result = compare_to_ground_truth(model, truth)
    >>> print(result.rank_correlation)
    0.866
    """
    # Find common channels
    channels = sorted(set(model_output.keys()) & set(true_effects.keys()))

    if len(channels) < 2:
        raise ValueError("Need at least 2 common channels to compare")

    model_values = np.array([model_output[c] for c in channels])
    true_values = np.array([true_effects[c] for c in channels])

    # 1. Rank correlation (do we get the order right?)
    spearman_rho, _ = stats.spearmanr(model_values, true_values)

    # 2. Magnitude error (how far off are the values?)
    # Use MAPE but handle zeros gracefully
    nonzero_mask = true_values > 1e-10
    if nonzero_mask.sum() > 0:
        mape = np.mean(np.abs(model_values[nonzero_mask] - true_values[nonzero_mask])
                       / true_values[nonzero_mask])
    else:
        mape = np.nan

    # 3. Top channel accuracy (do we pick the same winner?)
    model_winner = channels[np.argmax(model_values)]
    true_winner = channels[np.argmax(true_values)]
    top_match = (model_winner == true_winner)

    # 4. Top-k overlap
    k = min(3, len(channels))
    model_top_k = set(np.array(channels)[np.argsort(model_values)[-k:]])
    true_top_k = set(np.array(channels)[np.argsort(true_values)[-k:]])
    top_k_overlap = len(model_top_k & true_top_k) / k

    # 5. Confidence calibration (if CIs provided)
    calibration = np.nan
    if model_confidence_intervals is not None:
        coverage_count = 0
        total_count = 0
        for c in channels:
            if c in model_confidence_intervals:
                lower, upper = model_confidence_intervals[c]
                true_val = true_effects[c]
                if lower <= true_val <= upper:
                    coverage_count += 1
                total_count += 1
        if total_count > 0:
            # For 90% CI, we expect ~90% coverage
            actual_coverage = coverage_count / total_count
            # Calibration: how close to expected 0.90?
            calibration = 1.0 - abs(0.90 - actual_coverage)

    return ValidationResult(
        rank_correlation=spearman_rho,
        magnitude_error=mape,
        top_channel_match=top_match,
        top_k_overlap=top_k_overlap,
        confidence_calibration=calibration
    )


def compare_against_baselines(
    model_output: Dict[str, float],
    journey_data: List[Dict],
    true_effects: Dict[str, float]
) -> Dict[str, ValidationResult]:
    """
    Compare model against heuristic baselines (last-touch, linear, time-decay).

    Parameters
    ----------
    model_output : dict
        Attribution from the Markov-Shapley model
    journey_data : list
        List of customer journeys, each with 'path' and 'conversion_value'
    true_effects : dict
        Ground truth causal effects

    Returns
    -------
    dict
        Model name -> ValidationResult
    """
    results = {}

    # Our model
    results['markov_shapley'] = compare_to_ground_truth(model_output, true_effects)

    # Last-touch baseline
    last_touch = calculate_last_touch_attribution(journey_data)
    results['last_touch'] = compare_to_ground_truth(last_touch, true_effects)

    # Linear baseline
    linear = calculate_linear_attribution(journey_data)
    results['linear'] = compare_to_ground_truth(linear, true_effects)

    # Time-decay baseline
    time_decay = calculate_time_decay_attribution(journey_data)
    results['time_decay'] = compare_to_ground_truth(time_decay, true_effects)

    return results


def calculate_last_touch_attribution(journey_data: List[Dict]) -> Dict[str, float]:
    """Last-touch: 100% credit to final touchpoint before conversion."""
    attribution = {}
    total_value = 0

    for journey in journey_data:
        if journey.get('converted', False) and journey.get('path'):
            last_channel = journey['path'][-1]
            value = journey.get('conversion_value', 1)
            attribution[last_channel] = attribution.get(last_channel, 0) + value
            total_value += value

    # Normalize to shares
    if total_value > 0:
        attribution = {k: v / total_value for k, v in attribution.items()}

    return attribution


def calculate_linear_attribution(journey_data: List[Dict]) -> Dict[str, float]:
    """Linear: Equal credit to all touchpoints."""
    attribution = {}
    total_value = 0

    for journey in journey_data:
        if journey.get('converted', False) and journey.get('path'):
            path = journey['path']
            value = journey.get('conversion_value', 1)
            credit_per_touch = value / len(path)

            for channel in path:
                attribution[channel] = attribution.get(channel, 0) + credit_per_touch
            total_value += value

    # Normalize to shares
    if total_value > 0:
        attribution = {k: v / total_value for k, v in attribution.items()}

    return attribution


def calculate_time_decay_attribution(
    journey_data: List[Dict],
    half_life: float = 7.0  # days
) -> Dict[str, float]:
    """Time-decay: More credit to recent touchpoints."""
    attribution = {}
    total_value = 0

    for journey in journey_data:
        if journey.get('converted', False) and journey.get('path'):
            path = journey['path']
            timestamps = journey.get('timestamps', list(range(len(path))))
            value = journey.get('conversion_value', 1)

            # Calculate decay weights (most recent = 1.0)
            if len(timestamps) > 1:
                max_time = max(timestamps)
                weights = [2 ** ((t - max_time) / half_life) for t in timestamps]
            else:
                weights = [1.0]

            # Normalize weights
            weight_sum = sum(weights)
            weights = [w / weight_sum for w in weights]

            # Distribute credit
            for channel, weight in zip(path, weights):
                attribution[channel] = attribution.get(channel, 0) + value * weight
            total_value += value

    # Normalize to shares
    if total_value > 0:
        attribution = {k: v / total_value for k, v in attribution.items()}

    return attribution


def generate_synthetic_ground_truth(
    n_journeys: int = 10000,
    channels: List[str] = None,
    true_effects: Dict[str, float] = None,
    noise_level: float = 0.1,
    seed: int = 42
) -> Tuple[List[Dict], Dict[str, float]]:
    """
    Generate synthetic journey data with known true causal effects.

    Useful for validating that the model recovers known effects.

    Parameters
    ----------
    n_journeys : int
        Number of journeys to generate
    channels : list
        Channel names
    true_effects : dict
        True causal contribution of each channel
    noise_level : float
        Amount of random noise (0 = deterministic)
    seed : int
        Random seed for reproducibility

    Returns
    -------
    journey_data : list
        Synthetic customer journeys
    true_effects : dict
        The ground truth effects used for generation
    """
    np.random.seed(seed)

    if channels is None:
        channels = ['Search', 'Email', 'Direct', 'Social', 'Display']

    if true_effects is None:
        # Default true effects (sum to 1)
        true_effects = {
            'Search': 0.35,
            'Email': 0.25,
            'Direct': 0.20,
            'Social': 0.12,
            'Display': 0.08
        }

    journeys = []

    for _ in range(n_journeys):
        # Random path length (1-6 touchpoints)
        path_length = np.random.randint(1, 7)

        # Random channel sequence
        path = list(np.random.choice(channels, size=path_length))

        # Conversion probability based on true effects
        # P(convert) = sum of effects for channels in path (capped at 0.95)
        unique_channels = set(path)
        base_prob = sum(true_effects.get(c, 0) for c in unique_channels)
        base_prob = min(0.95, base_prob)

        # Add noise
        prob = base_prob + np.random.normal(0, noise_level)
        prob = np.clip(prob, 0.01, 0.99)

        # Determine conversion
        converted = np.random.random() < prob

        journeys.append({
            'path': path,
            'converted': converted,
            'conversion_value': 100 if converted else 0,
            'timestamps': list(range(len(path)))
        })

    return journeys, true_effects


def run_validation_report(
    model_output: Dict[str, float],
    journey_data: List[Dict],
    true_effects: Dict[str, float],
    model_confidence_intervals: Optional[Dict[str, Tuple[float, float]]] = None
) -> str:
    """
    Generate a comprehensive validation report.

    Returns a formatted string suitable for inclusion in documentation.
    """
    # Get all comparison results
    our_result = compare_to_ground_truth(
        model_output, true_effects, model_confidence_intervals
    )
    baseline_results = compare_against_baselines(
        model_output, journey_data, true_effects
    )

    report = []
    report.append("=" * 60)
    report.append("ATTRIBUTION MODEL VALIDATION REPORT")
    report.append("=" * 60)
    report.append("")

    # Model performance
    report.append("## Markov-Shapley Model Performance")
    report.append(f"  Rank Correlation (Spearman):  {our_result.rank_correlation:.3f}")
    report.append(f"  Magnitude Error (MAPE):       {our_result.magnitude_error:.1%}")
    report.append(f"  Top Channel Match:            {'Yes' if our_result.top_channel_match else 'No'}")
    report.append(f"  Top-3 Overlap:                {our_result.top_k_overlap:.0%}")
    if not np.isnan(our_result.confidence_calibration):
        report.append(f"  CI Calibration:               {our_result.confidence_calibration:.3f}")
    report.append("")

    # Baseline comparison
    report.append("## Comparison vs Baselines")
    report.append("-" * 50)
    report.append(f"{'Model':<20} {'Rank Corr':>10} {'MAPE':>10} {'Top Match':>10}")
    report.append("-" * 50)

    for name, result in baseline_results.items():
        top_str = "Yes" if result.top_channel_match else "No"
        report.append(
            f"{name:<20} {result.rank_correlation:>10.3f} "
            f"{result.magnitude_error:>9.1%} {top_str:>10}"
        )

    report.append("-" * 50)
    report.append("")

    # Interpretation
    report.append("## Interpretation")

    # Is our model better than baselines?
    our_rho = baseline_results['markov_shapley'].rank_correlation
    best_baseline_rho = max(
        baseline_results['last_touch'].rank_correlation,
        baseline_results['linear'].rank_correlation,
        baseline_results['time_decay'].rank_correlation
    )

    if our_rho > best_baseline_rho:
        improvement = (our_rho - best_baseline_rho) / abs(best_baseline_rho) * 100
        report.append(f"  ✓ Markov-Shapley outperforms baselines by {improvement:.0f}% on rank correlation")
    else:
        report.append("  ⚠ Markov-Shapley does not outperform all baselines on this dataset")

    if our_result.top_channel_match:
        report.append("  ✓ Model correctly identifies the top contributing channel")
    else:
        report.append("  ⚠ Model does not identify the correct top channel")

    report.append("")
    report.append("## Caveats")
    report.append("  • This validation measures CONTRIBUTION accuracy, not CAUSATION")
    report.append("  • True causal effects require randomized experiments")
    report.append("  • See WHITEPAPER.md 'Limitations and Causal Interpretation'")
    report.append("")

    return "\n".join(report)


if __name__ == "__main__":
    # Demo: validate model against synthetic ground truth
    print("Generating synthetic data with known true effects...")
    journeys, true_effects = generate_synthetic_ground_truth(n_journeys=5000)

    print(f"True effects: {true_effects}")
    print(f"Generated {len(journeys)} journeys")
    print(f"Conversion rate: {sum(1 for j in journeys if j['converted']) / len(journeys):.1%}")
    print()

    # Simulate model output (with some error)
    model_output = {
        'Search': 0.38,   # True: 0.35
        'Email': 0.22,    # True: 0.25
        'Direct': 0.21,   # True: 0.20
        'Social': 0.11,   # True: 0.12
        'Display': 0.08   # True: 0.08
    }

    model_cis = {
        'Search': (0.32, 0.44),
        'Email': (0.18, 0.28),
        'Direct': (0.16, 0.26),
        'Social': (0.07, 0.15),
        'Display': (0.04, 0.12)
    }

    report = run_validation_report(
        model_output, journeys, true_effects, model_cis
    )
    print(report)
