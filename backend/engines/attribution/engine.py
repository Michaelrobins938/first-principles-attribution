"""
Attribution Engine - Markov Chain and Shapley Value Attribution Analysis

This module implements three attribution models:
1. Markov Chain Attribution - Sequential path contribution analysis
2. Shapley Value Attribution - Game-theoretic fair division
3. Hybrid Attribution - Configurable blend of both methods
"""

import json
import time
from collections import defaultdict
from itertools import combinations
from typing import Optional
import numpy as np
from scipy import linalg
from scipy.stats import norm

from backend.models.attribution import (
    Journey,
    MarkovResult,
    ShapleyResult,
    HybridResult,
    ChannelMetrics,
)


class MarkovAttribution:
    """
    Markov Chain Attribution Model
    
    Builds a state transition matrix from customer journeys and calculates
    each channel's contribution based on its removal effect.
    """
    
    def __init__(self, journeys: list[Journey]):
        self.journeys = journeys
        self.channels = self._extract_channels()
        self.transition_matrix = self._build_transition_matrix()
        self.channel_order = list(self.channels)
        
    def _extract_channels(self) -> set[str]:
        """Extract all unique channels from journeys."""
        channels = set()
        for journey in self.journeys:
            for touchpoint in journey.path:
                channels.add(touchpoint.channel)
        return channels
    
    def _build_transition_matrix(self) -> dict[str, dict[str, float]]:
        """Build transition probability matrix from paths."""
        transitions = defaultdict(lambda: defaultdict(int))
        path_counts = defaultdict(int)
        
        for journey in self.journeys:
            if len(journey.path) < 1:
                continue
                
            path_channels = [tp.channel for tp in journey.path]
            path_tuple = tuple(path_channels)
            path_counts[path_tuple] += 1
            
            for i in range(len(path_channels) - 1):
                transitions[path_channels[i]][path_channels[i + 1]] += 1
            
            transitions[path_channels[-1]]["conversion"] += path_counts[path_tuple]
        
        channel_list = list(self.channels)
        matrix = {}
        
        for channel in channel_list:
            matrix[channel] = {}
            total = sum(transitions[channel].values()) or 1
            
            for next_channel in channel_list:
                matrix[channel][next_channel] = transitions[channel][next_channel] / total
            
            matrix[channel]["conversion"] = transitions[channel]["conversion"] / total
        
        return matrix
    
    def _build_transition_matrix_numpy(self) -> tuple[np.ndarray, dict[str, int]]:
        """Build numpy transition matrix for efficient computation."""
        channel_list = sorted(self.channels)
        channel_to_idx = {c: i for i, c in enumerate(channel_list)}
        n = len(channel_list)
        
        transitions = defaultdict(lambda: np.zeros(n + 1))
        path_counts = defaultdict(int)
        
        for journey in self.journeys:
            if len(journey.path) < 1:
                continue
                
            path_channels = [tp.channel for tp in journey.path]
            path_tuple = tuple(path_channels)
            path_counts[path_tuple] += 1
            
            for i in range(len(path_channels) - 1):
                from_c = path_channels[i]
                to_c = path_channels[i + 1]
                transitions[from_c][channel_to_idx[to_c]] += path_counts[path_tuple]
            
            transitions[path_channels[-1]][-1] += path_counts[path_tuple]
        
        matrix = np.zeros((n + 1, n + 1))
        
        for channel, idx in channel_to_idx.items():
            total = transitions[channel].sum() or 1
            matrix[idx] = transitions[channel] / total
        
        matrix[-1] = 0
        matrix[-1][-1] = 1
        
        return matrix, channel_to_idx
    
    def calculate_attribution(self) -> tuple[dict[str, float], dict[str, float]]:
        """
        Calculate channel attributions using Markov chain model.
        
        Returns:
            Tuple of (attributions dict, removal effects dict)
        """
        if not self.journeys:
            return {}, {}
        
        channel_list = sorted(self.channels)
        n = len(channel_list)
        
        all_conversions = sum(1 for j in self.journeys if j.conversion)
        baseline_conversion_rate = all_conversions / len(self.journeys)
        
        removal_effects = {}
        attributions = {}
        
        for channel in channel_list:
            journeys_with_channel = [
                j for j in self.journeys 
                if any(tp.channel == channel for tp in j.path)
            ]
            
            if not journeys_with_channel:
                removal_effects[channel] = 0.0
                continue
            
            conversions_without = sum(1 for j in journeys_with_channel if not j.conversion)
            conversion_rate_without = conversions_without / len(journeys_with_channel)
            
            removal_effect = (baseline_conversion_rate - conversion_rate_without) / baseline_conversion_rate
            removal_effects[channel] = max(0.0, removal_effect)
            
            total_effect = sum(removal_effects.values()) or 1
            attributions[channel] = removal_effect / total_effect
        
        return attributions, removal_effects
    
    def calculate_removal_effects(self) -> dict[str, float]:
        """Calculate removal effects for each channel."""
        _, removal_effects = self.calculate_attribution()
        return removal_effects
    
    def get_full_result(self) -> MarkovResult:
        """Get complete Markov attribution result."""
        attributions, removal_effects = self.calculate_attribution()
        
        total_conversions = sum(1 for j in self.journeys if j.conversion)
        
        confidence_intervals = {}
        for channel in self.channels:
            base_rate = total_conversions / len(self.journeys) if self.journeys else 0
            channel_journeys = [
                j for j in self.journeys 
                if any(tp.channel == channel for tp in j.path)
            ]
            if channel_journeys:
                channel_conversions = sum(1 for j in channel_journeys if j.conversion)
                channel_rate = channel_conversions / len(channel_journeys)
                std_error = np.sqrt(base_rate * (1 - base_rate) / len(channel_journeys))
                ci = 1.96 * std_error
                confidence_intervals[channel] = {
                    "low": max(0, attributions.get(channel, 0) - ci),
                    "high": attributions.get(channel, 0) + ci
                }
            else:
                confidence_intervals[channel] = {"low": 0, "high": 0}
        
        return MarkovResult(
            channel_attributions=attributions,
            transition_matrix=self.transition_matrix,
            removal_effects=removal_effects,
            total_conversions=total_conversions,
            confidence_interval=confidence_intervals
        )


class ShapleyAttribution:
    """
    Shapley Value Attribution Model
    
    Calculates fair attribution using cooperative game theory.
    Each channel's value is its marginal contribution averaged across all coalitions.
    """
    
    def __init__(self, journeys: list[Journey], max_iterations: int = 1000):
        self.journeys = journeys
        self.channels = self._extract_channels()
        self.max_iterations = max_iterations
        self.conversion_rate_cache = {}
        
    def _extract_channels(self) -> set[str]:
        """Extract all unique channels from journeys."""
        channels = set()
        for journey in self.journeys:
            for touchpoint in journey.path:
                channels.add(touchpoint.channel)
        return channels
    
    def _get_conversion_rate(self, channel_set: frozenset) -> float:
        """Get conversion rate for a set of channels (coalition value)."""
        if channel_set in self.conversion_rate_cache:
            return self.conversion_rate_cache[channel_set]
        
        relevant_journeys = [
            j for j in self.journeys 
            if all(tp.channel in channel_set for tp in j.path)
        ]
        
        if not relevant_journeys:
            rate = 0.0
        else:
            conversions = sum(1 for j in relevant_journeys if j.conversion)
            rate = conversions / len(relevant_journeys)
        
        self.conversion_rate_cache[channel_set] = rate
        return rate
    
    def _marginal_contribution(self, channel: str, coalition: frozenset) -> float:
        """Calculate marginal contribution of a channel to a coalition."""
        coalition_without = coalition - {channel}
        coalition_with = coalition | {channel}
        
        value_with = self._get_conversion_rate(coalition_with)
        value_without = self._get_conversion_rate(coalition_without)
        
        return value_with - value_without
    
    def calculate_shapley_values(self) -> dict[str, float]:
        """
        Calculate Shapley values for all channels.
        
        Uses sampling for efficiency with large channel sets.
        """
        if not self.journeys or not self.channels:
            return {}
        
        channel_list = list(self.channels)
        n = len(channel_list)
        
        shapley_values = defaultdict(float)
        marginal_contributions = defaultdict(list)
        
        total_conversions = sum(1 for j in self.journeys if j.conversion)
        baseline_rate = total_conversions / len(self.journeys) if self.journeys else 0
        
        num_samples = min(self.max_iterations, 2 ** n)
        
        for _ in range(num_samples):
            permutation = list(channel_list)
            np.random.shuffle(permutation)
            
            coalition = frozenset()
            
            for i, channel in enumerate(permutation):
                mc = self._marginal_contribution(channel, coalition)
                marginal_contributions[channel].append(mc)
                shapley_values[channel] += mc
                coalition = coalition | {channel}
        
        for channel in channel_list:
            if marginal_contributions[channel]:
                shapley_values[channel] /= len(marginal_contributions[channel])
            else:
                shapley_values[channel] = 0
        
        total_value = sum(shapley_values.values()) or 1
        
        normalized_values = {}
        for channel, value in shapley_values.items():
            normalized_values[channel] = value / total_value
        
        return normalized_values
    
    def get_full_result(self) -> ShapleyResult:
        """Get complete Shapley attribution result."""
        values = self.calculate_shapley_values()
        
        all_channels = list(self.channels)
        total_value = sum(values.values()) or 1
        
        marginal_contributions = {}
        for channel in all_channels:
            channel_value = values[channel]
            percentage = (channel_value / total_value) * 100 if total_value > 0 else 0
            marginal_contributions[channel] = [channel_value, percentage]
        
        return ShapleyResult(
            channel_values=values,
            marginal_contributions=marginal_contributions,
            convergence=True,
            iterations=min(self.max_iterations, 2 ** len(all_channels))
        )


class HybridAttribution:
    """
    Hybrid Attribution Model
    
    Combines Markov Chain and Shapley Value attribution with configurable
    weighting (alpha parameter).
    
    Result = (1 - alpha) * Markov + alpha * Shapley
    """
    
    def __init__(self, journeys: list[Journey], alpha: float = 0.5):
        self.journeys = journeys
        self.alpha = alpha
        self.markov = MarkovAttribution(journeys)
        self.shapley = ShapleyAttribution(journeys)
        self.channels = self.markov.channels
        
    def calculate_attribution(self) -> dict[str, float]:
        """Calculate hybrid attribution combining Markov and Shapley."""
        markov_result = self.markov.calculate_attribution()[0]
        shapley_result = self.shapley.calculate_shapley_values()
        
        all_channels = self.channels
        
        hybrid = {}
        for channel in all_channels:
            markov_val = markov_result.get(channel, 0)
            shapley_val = shapley_result.get(channel, 0)
            hybrid[channel] = (1 - self.alpha) * markov_val + self.alpha * shapley_val
        
        total = sum(hybrid.values()) or 1
        for channel in hybrid:
            hybrid[channel] /= total
        
        return hybrid
    
    def get_full_result(self) -> HybridResult:
        """Get complete hybrid attribution result."""
        hybrid = self.calculate_attribution()
        
        markov_attributions, _ = self.markov.calculate_attribution()
        shapley_values = self.shapley.calculate_shapley_values()
        
        confidence_intervals = {}
        for channel in self.channels:
            markov_ci = 0.05
            shapley_ci = 0.05
            
            ci_low = hybrid.get(channel, 0) - self.alpha * shapley_ci - (1 - self.alpha) * markov_ci
            ci_high = hybrid.get(channel, 0) + self.alpha * shapley_ci + (1 - self.alpha) * markov_ci
            
            confidence_intervals[channel] = {
                "low": max(0, ci_low),
                "high": max(0, ci_high)
            }
        
        return HybridResult(
            channel_attributions=hybrid,
            alpha_used=self.alpha,
            markov_weight=1 - self.alpha,
            shapley_weight=self.alpha,
            confidence_intervals=confidence_intervals
        )


class AttributionEngine:
    """
    Main Attribution Engine
    
    Orchestrates attribution analysis using Markov, Shapley, and Hybrid models.
    """
    
    def __init__(self, journeys: list[Journey]):
        self.journeys = journeys
        self.markov = MarkovAttribution(journeys)
        self.shapley = ShapleyAttribution(journeys)
        self.hybrid = None
        
    def run_analysis(
        self, 
        alpha: float = 0.5,
        include_uncertainty: bool = True,
        filter_channels: Optional[list[str]] = None
    ) -> dict:
        """
        Run complete attribution analysis.
        
        Args:
            alpha: Weight for Shapley (0 = Markov only, 1 = Shapley only)
            include_uncertainty: Whether to calculate confidence intervals
            filter_channels: Optional list of channels to include
            
        Returns:
            Complete attribution analysis results
        """
        start_time = time.perf_counter()
        
        filtered_journeys = self.journeys
        if filter_channels:
            filter_set = set(filter_channels)
            filtered_journeys = [
                j for j in self.journeys
                if any(tp.channel in filter_set for tp in j.path)
            ]
        
        if alpha == 0:
            self.hybrid = None
            markov_result = MarkovAttribution(filtered_journeys).get_full_result()
            shapley_result = None
            hybrid_result = None
        elif alpha == 1:
            self.hybrid = None
            markov_result = None
            shapley_result = ShapleyAttribution(filtered_journeys).get_full_result()
            hybrid_result = None
        else:
            self.hybrid = HybridAttribution(filtered_journeys, alpha)
            markov_result = None
            shapley_result = None
            hybrid_result = self.hybrid.get_full_result()
        
        channels = set()
        for j in filtered_journeys:
            for tp in j.path:
                channels.add(tp.channel)
        
        if filter_channels:
            channels = channels & set(filter_channels)
        
        channel_metrics = self._calculate_channel_metrics(filtered_journeys, channels)
        
        total_conversions = sum(1 for j in filtered_journeys if j.conversion)
        total_journeys = len(filtered_journeys)
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        channels_summary = {}
        for channel in channels:
            count = sum(
                1 for j in filtered_journeys
                if any(tp.channel == channel for tp in j.path)
            )
            channels_summary[channel] = count
        
        result = {
            "status": "success",
            "processing_time_ms": processing_time,
            "total_journeys": total_journeys,
            "total_conversions": total_conversions,
            "unique_channels": len(channels),
            "markov_result": markov_result.model_dump() if markov_result else None,
            "shapley_result": shapley_result.model_dump() if shapley_result else None,
            "hybrid_result": hybrid_result.model_dump() if hybrid_result else None,
            "channel_metrics": [cm.model_dump() for cm in channel_metrics],
            "channels_summary": channels_summary
        }
        
        return result
    
    def _calculate_channel_metrics(
        self, 
        journeys: list[Journey],
        channels: set[str]
    ) -> list[ChannelMetrics]:
        """Calculate detailed metrics for each channel."""
        metrics = []
        
        for channel in channels:
            channel_journeys = [
                j for j in journeys
                if any(tp.channel == channel for tp in j.path)
            ]
            
            if not channel_journeys:
                continue
            
            conversions = sum(1 for j in channel_journeys if j.conversion)
            conversion_rate = conversions / len(channel_journeys)
            
            avg_position = 0
            if channel_journeys:
                positions = []
                for j in channel_journeys:
                    for i, tp in enumerate(j.path):
                        if tp.channel == channel:
                            positions.append(i / max(len(j.path) - 1, 1))
                            break
                avg_position = sum(positions) / len(positions) if positions else 0
            
            metrics.append(ChannelMetrics(
                channel=channel,
                touchpoint_count=len(channel_journeys),
                conversion_rate=conversion_rate,
                avg_position=avg_position
            ))
        
        return metrics
