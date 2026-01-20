"""
Weight Learning Module for First-Principles Attribution

Learn psychographic/context weights from data rather than hand-tuning.
Uses cross-validation to find weights that maximize conversion prediction accuracy.

Usage:
    python weight_learning.py --data journeys.json --method cv --folds 5
"""

import numpy as np
from scipy import optimize
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass
from itertools import product
import json


@dataclass
class LearningResult:
    """Results from weight optimization."""
    optimal_weights: Dict[str, float]
    cv_score: float
    method: str
    iterations: int
    convergence_history: List[float]

    def to_dict(self) -> dict:
        return {
            'optimal_weights': self.optimal_weights,
            'cv_score': self.cv_score,
            'method': self.method,
            'iterations': self.iterations,
            'convergence_history': self.convergence_history
        }


# Default context categories with initial weights
DEFAULT_CONTEXT_WEIGHTS = {
    'device': {
        'mobile': 1.0,
        'desktop': 1.2,
        'tablet': 1.1
    },
    'intent_signal': {
        'high': 1.5,
        'medium': 1.0,
        'low': 0.7
    },
    'session_depth': {
        'shallow': 0.8,  # 1-2 pages
        'medium': 1.0,   # 3-5 pages
        'deep': 1.3      # 6+ pages
    },
    'time_of_day': {
        'morning': 1.0,
        'afternoon': 1.1,
        'evening': 1.2,
        'night': 0.9
    }
}


def flatten_weights(nested_weights: Dict[str, Dict[str, float]]) -> np.ndarray:
    """Convert nested weight dict to flat array for optimization."""
    flat = []
    for category in sorted(nested_weights.keys()):
        for level in sorted(nested_weights[category].keys()):
            flat.append(nested_weights[category][level])
    return np.array(flat)


def unflatten_weights(
    flat_weights: np.ndarray,
    template: Dict[str, Dict[str, float]]
) -> Dict[str, Dict[str, float]]:
    """Convert flat array back to nested weight dict."""
    result = {}
    idx = 0
    for category in sorted(template.keys()):
        result[category] = {}
        for level in sorted(template[category].keys()):
            result[category][level] = float(flat_weights[idx])
            idx += 1
    return result


def calculate_transition_weight(
    event: Dict,
    weights: Dict[str, Dict[str, float]]
) -> float:
    """
    Calculate the transition weight for an event based on context.

    Parameters
    ----------
    event : dict
        Event with context fields (device, intent_signal, etc.)
    weights : dict
        Nested weight dictionary

    Returns
    -------
    float
        Combined weight multiplier
    """
    combined_weight = 1.0

    context = event.get('context', {})

    for category, levels in weights.items():
        value = context.get(category)
        if value and value in levels:
            combined_weight *= levels[value]

    return combined_weight


def build_weighted_transition_matrix(
    events: List[Dict],
    weights: Dict[str, Dict[str, float]],
    channels: List[str]
) -> np.ndarray:
    """
    Build transition matrix with context-weighted transitions.

    Parameters
    ----------
    events : list
        List of events with channel, context, and user_id
    weights : dict
        Context weights to apply
    channels : list
        Ordered list of channel names

    Returns
    -------
    np.ndarray
        Row-stochastic transition matrix
    """
    n = len(channels)
    channel_idx = {c: i for i, c in enumerate(channels)}

    # Count weighted transitions
    T = np.zeros((n + 2, n + 2))  # +2 for START and CONVERT states

    # Group events by user
    user_events = {}
    for e in events:
        uid = e.get('user_id', 'unknown')
        if uid not in user_events:
            user_events[uid] = []
        user_events[uid].append(e)

    # Process journeys
    START_IDX = n
    CONVERT_IDX = n + 1

    for uid, journey in user_events.items():
        # Sort by timestamp
        journey = sorted(journey, key=lambda x: x.get('timestamp', 0))

        prev_idx = START_IDX

        for event in journey:
            channel = event.get('channel')
            if channel not in channel_idx:
                continue

            curr_idx = channel_idx[channel]
            weight = calculate_transition_weight(event, weights)

            T[prev_idx, curr_idx] += weight
            prev_idx = curr_idx

            # Check for conversion
            if event.get('event_type') == 'conversion':
                T[curr_idx, CONVERT_IDX] += weight

    # Make row-stochastic
    row_sums = T.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # Avoid division by zero
    T = T / row_sums

    return T


def predict_conversion_probability(
    T: np.ndarray,
    max_steps: int = 20
) -> float:
    """
    Calculate conversion probability from transition matrix.

    Uses absorbing Markov chain analysis.
    """
    n = T.shape[0] - 2
    CONVERT_IDX = n + 1

    # Start from START state, calculate probability of reaching CONVERT
    state = np.zeros(T.shape[0])
    state[n] = 1.0  # START state

    for _ in range(max_steps):
        state = state @ T

    return state[CONVERT_IDX]


def calculate_prediction_error(
    events: List[Dict],
    weights: Dict[str, Dict[str, float]],
    channels: List[str]
) -> float:
    """
    Calculate prediction error for given weights.

    Returns negative log-likelihood (lower is better).
    """
    T = build_weighted_transition_matrix(events, weights, channels)
    pred_prob = predict_conversion_probability(T)

    # Count actual conversions
    actual_conversions = sum(
        1 for e in events if e.get('event_type') == 'conversion'
    )
    total_journeys = len(set(e.get('user_id') for e in events))

    if total_journeys == 0:
        return float('inf')

    actual_rate = actual_conversions / total_journeys

    # Log-likelihood (avoid log(0))
    pred_prob = np.clip(pred_prob, 1e-10, 1 - 1e-10)
    actual_rate = np.clip(actual_rate, 1e-10, 1 - 1e-10)

    # Cross-entropy loss
    loss = -(actual_rate * np.log(pred_prob) +
             (1 - actual_rate) * np.log(1 - pred_prob))

    return loss


def k_fold_split(
    events: List[Dict],
    k: int = 5,
    seed: int = 42
) -> List[Tuple[List[Dict], List[Dict]]]:
    """
    Split events into k folds by user_id.

    Returns list of (train, test) tuples.
    """
    np.random.seed(seed)

    # Group by user
    user_events = {}
    for e in events:
        uid = e.get('user_id', 'unknown')
        if uid not in user_events:
            user_events[uid] = []
        user_events[uid].append(e)

    # Shuffle users
    users = list(user_events.keys())
    np.random.shuffle(users)

    # Create folds
    fold_size = len(users) // k
    folds = []

    for i in range(k):
        start = i * fold_size
        end = start + fold_size if i < k - 1 else len(users)
        test_users = set(users[start:end])
        train_users = set(users) - test_users

        train_events = [e for uid in train_users for e in user_events[uid]]
        test_events = [e for uid in test_users for e in user_events[uid]]

        folds.append((train_events, test_events))

    return folds


def tune_weights_cv(
    events: List[Dict],
    channels: List[str],
    k_folds: int = 5,
    weight_bounds: Tuple[float, float] = (0.1, 3.0),
    method: str = 'grid',
    grid_resolution: int = 3,
    verbose: bool = True
) -> LearningResult:
    """
    Find weights that minimize prediction error on held-out conversions.

    Parameters
    ----------
    events : list
        Event data with context fields
    channels : list
        Channel names
    k_folds : int
        Number of cross-validation folds
    weight_bounds : tuple
        (min, max) bounds for weight values
    method : str
        'grid' for grid search, 'optimize' for scipy optimization
    grid_resolution : int
        Points per dimension for grid search
    verbose : bool
        Print progress

    Returns
    -------
    LearningResult
        Optimal weights and metadata
    """
    template = DEFAULT_CONTEXT_WEIGHTS
    folds = k_fold_split(events, k_folds)

    if verbose:
        print(f"Running {k_folds}-fold cross-validation...")
        print(f"Method: {method}, Bounds: {weight_bounds}")

    best_score = float('inf')
    best_weights = None
    history = []
    iterations = 0

    if method == 'grid':
        # Grid search over simplified weight space
        # (full grid would be too large, so we search key dimensions)
        grid_values = np.linspace(weight_bounds[0], weight_bounds[1], grid_resolution)

        # Search over intent_signal weights (most important)
        for high_w, med_w, low_w in product(grid_values, repeat=3):
            iterations += 1
            test_weights = {
                'device': {'mobile': 1.0, 'desktop': 1.2, 'tablet': 1.1},
                'intent_signal': {'high': high_w, 'medium': med_w, 'low': low_w},
                'session_depth': {'shallow': 0.8, 'medium': 1.0, 'deep': 1.3},
                'time_of_day': {'morning': 1.0, 'afternoon': 1.1, 'evening': 1.2, 'night': 0.9}
            }

            # Cross-validation score
            cv_scores = []
            for train, test in folds:
                # Train: build matrix with these weights
                # Test: evaluate prediction error
                train_error = calculate_prediction_error(train, test_weights, channels)
                test_error = calculate_prediction_error(test, test_weights, channels)
                cv_scores.append(test_error)

            mean_score = np.mean(cv_scores)
            history.append(mean_score)

            if mean_score < best_score:
                best_score = mean_score
                best_weights = test_weights
                if verbose:
                    print(f"  New best: score={mean_score:.4f}, "
                          f"intent=[{high_w:.1f}, {med_w:.1f}, {low_w:.1f}]")

    elif method == 'optimize':
        # Scipy optimization
        initial = flatten_weights(template)

        def objective(flat_weights):
            weights = unflatten_weights(flat_weights, template)
            scores = []
            for train, test in folds:
                error = calculate_prediction_error(test, weights, channels)
                scores.append(error)
            return np.mean(scores)

        bounds = [(weight_bounds[0], weight_bounds[1])] * len(initial)

        result = optimize.minimize(
            objective,
            initial,
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': 100, 'disp': verbose}
        )

        best_weights = unflatten_weights(result.x, template)
        best_score = result.fun
        iterations = result.nit
        history = [best_score]  # Only final score available

    if verbose:
        print(f"\nOptimization complete!")
        print(f"Best CV score: {best_score:.4f}")
        print(f"Iterations: {iterations}")

    return LearningResult(
        optimal_weights=best_weights,
        cv_score=best_score,
        method=method,
        iterations=iterations,
        convergence_history=history
    )


def tune_weights_mle(
    events: List[Dict],
    channels: List[str],
    weight_bounds: Tuple[float, float] = (0.1, 3.0),
    verbose: bool = True
) -> LearningResult:
    """
    Find weights via Maximum Likelihood Estimation.

    Maximizes the likelihood of observed conversion outcomes.

    Parameters
    ----------
    events : list
        Event data
    channels : list
        Channel names
    weight_bounds : tuple
        (min, max) bounds
    verbose : bool
        Print progress

    Returns
    -------
    LearningResult
    """
    template = DEFAULT_CONTEXT_WEIGHTS
    initial = flatten_weights(template)

    history = []

    def negative_log_likelihood(flat_weights):
        weights = unflatten_weights(flat_weights, template)
        nll = calculate_prediction_error(events, weights, channels)
        history.append(nll)
        return nll

    bounds = [(weight_bounds[0], weight_bounds[1])] * len(initial)

    if verbose:
        print("Running MLE optimization...")

    result = optimize.minimize(
        negative_log_likelihood,
        initial,
        method='L-BFGS-B',
        bounds=bounds,
        options={'maxiter': 200, 'disp': verbose}
    )

    best_weights = unflatten_weights(result.x, template)

    if verbose:
        print(f"\nMLE complete!")
        print(f"Final NLL: {result.fun:.4f}")
        print(f"Iterations: {result.nit}")

    return LearningResult(
        optimal_weights=best_weights,
        cv_score=result.fun,
        method='mle',
        iterations=result.nit,
        convergence_history=history
    )


def save_learned_weights(result: LearningResult, filepath: str):
    """Save learned weights to JSON file."""
    output = {
        'weights': result.optimal_weights,
        'metadata': {
            'method': result.method,
            'cv_score': result.cv_score,
            'iterations': result.iterations
        }
    }
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)


def load_learned_weights(filepath: str) -> Dict[str, Dict[str, float]]:
    """Load weights from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data['weights']


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Learn context weights from data')
    parser.add_argument('--data', type=str, help='Path to journey data JSON')
    parser.add_argument('--method', type=str, default='cv', choices=['cv', 'mle', 'grid'],
                        help='Optimization method')
    parser.add_argument('--folds', type=int, default=5, help='Number of CV folds')
    parser.add_argument('--output', type=str, default='learned_weights.json',
                        help='Output file for learned weights')

    args = parser.parse_args()

    # Demo with synthetic data if no data file provided
    if not args.data:
        print("No data file provided. Running demo with synthetic data...")
        print()

        # Generate synthetic events
        np.random.seed(42)
        channels = ['Search', 'Email', 'Direct', 'Social', 'Display']
        events = []

        for user_id in range(500):
            n_events = np.random.randint(1, 8)
            for i in range(n_events):
                event = {
                    'user_id': f'user_{user_id}',
                    'timestamp': i,
                    'channel': np.random.choice(channels),
                    'event_type': 'click',
                    'context': {
                        'device': np.random.choice(['mobile', 'desktop', 'tablet']),
                        'intent_signal': np.random.choice(['high', 'medium', 'low']),
                        'session_depth': np.random.choice(['shallow', 'medium', 'deep'])
                    }
                }
                events.append(event)

            # Add conversion with probability based on context
            if np.random.random() < 0.3:
                events.append({
                    'user_id': f'user_{user_id}',
                    'timestamp': n_events,
                    'channel': events[-1]['channel'],
                    'event_type': 'conversion',
                    'context': events[-1]['context']
                })

        print(f"Generated {len(events)} events for {500} users")
        print()

        # Run CV optimization
        result = tune_weights_cv(
            events, channels,
            k_folds=args.folds,
            method='grid',
            grid_resolution=3,
            verbose=True
        )

        print("\n" + "=" * 50)
        print("LEARNED WEIGHTS")
        print("=" * 50)
        for category, levels in sorted(result.optimal_weights.items()):
            print(f"\n{category}:")
            for level, weight in sorted(levels.items()):
                print(f"  {level}: {weight:.2f}")

        # Save
        save_learned_weights(result, args.output)
        print(f"\nWeights saved to: {args.output}")

    else:
        # Load and process real data
        with open(args.data, 'r') as f:
            data = json.load(f)

        events = data.get('events', data)
        channels = list(set(e['channel'] for e in events if 'channel' in e))

        if args.method == 'mle':
            result = tune_weights_mle(events, channels, verbose=True)
        else:
            result = tune_weights_cv(events, channels, k_folds=args.folds, verbose=True)

        save_learned_weights(result, args.output)
        print(f"\nWeights saved to: {args.output}")
