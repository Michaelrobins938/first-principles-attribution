"""
Kelley Covariation Model Implementation

This module implements the covariation model for distinguishing between
internal (dispositional) and external (situational) attributions.

Based on Kelley's (1973) Covariation Model and Jones & Davis (1965) Correspondence Inference Theory.

The model analyzes three key metrics:
1. CONSENSUS: Do others behave the same way in this situation?
2. DISTINCTIVENESS: Does the person only behave this way with this stimulus?
3. CONSISTENCY: Does the person behave this way every time this situation occurs?

Attribution Categories:
- INTERNAL (Dispositional): Low Consensus + Low Distinctiveness + High Consistency
- EXTERNAL (Situational): High Consensus + High Distinctiveness + High Consistency
- AMBIGUOUS: Any other combination
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import math


class AttributionType(Enum):
    INTERNAL = "dispositional"
    EXTERNAL = "situational"
    AMBIGUOUS = "ambiguous"


class AttributionConfidence(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Observation:
    actor: str
    action: str
    stimulus: str
    context: str
    timestamp: str
    others_behaved_same: bool = False
    alternative_stimuli_available: bool = True
    previous_occurrences: int = 0
    total_situation_occurrences: int = 0


@dataclass
class CovariationMetrics:
    consensus: float
    distinctiveness: float
    consistency: float
    
    def to_dict(self) -> dict:
        return {
            "consensus": self.consensus,
            "distinctiveness": self.distinctiveness,
            "consistency": self.consistency
        }


@dataclass  
class CovariationResult:
    attribution_type: AttributionType
    confidence: AttributionConfidence
    metrics: CovariationMetrics
    reasoning: list[str]
    
    def to_dict(self) -> dict:
        return {
            "attribution_type": self.attribution_type.value,
            "confidence": self.confidence.value,
            "metrics": self.metrics.to_dict(),
            "reasoning": self.reasoning,
            "summary": self.generate_summary()
        }
    
    def generate_summary(self) -> str:
        if self.attribution_type == AttributionType.INTERNAL:
            return f"INTERNAL ({self.confidence.value} confidence): Core behavioral pattern driven by personal disposition."
        elif self.attribution_type == AttributionType.EXTERNAL:
            return f"EXTERNAL ({self.confidence.value} confidence): Situational response driven by environmental context."
        return "AMBIGUOUS: Insufficient data for clear attribution."


@dataclass
class BehaviorProfile:
    behavior: str
    internal_indicators: list[str] = field(default_factory=list)
    external_indicators: list[str] = field(default_factory=list)
    observations: list[Observation] = field(default_factory=list)
    
    def add_observation(self, obs: Observation):
        self.observations.append(obs)
    
    def analyze(self, consensus_thresh: float = 0.3, 
                distinctiveness_thresh: float = 0.5,
                consistency_thresh: float = 0.7) -> CovariationResult:
        """Analyze the behavior profile using covariation model."""
        
        if not self.observations:
            return CovariationResult(
                attribution_type=AttributionType.AMBIGUOUS,
                confidence=AttributionConfidence.LOW,
                metrics=CovariationMetrics(0.0, 0.0, 0.0),
                reasoning=["No observations available for analysis"]
            )
        
        metrics = self._calculate_metrics()
        reasoning = self._generate_reasoning(metrics)
        
        attribution = self._determine_attribution(
            metrics, consensus_thresh, distinctiveness_thresh, consistency_thresh
        )
        confidence = self._calculate_confidence(metrics)
        
        return CovariationResult(
            attribution_type=attribution,
            confidence=confidence,
            metrics=metrics,
            reasoning=reasoning
        )
    
    def _calculate_metrics(self) -> CovariationMetrics:
        """Calculate the three covariation metrics."""
        n = len(self.observations)
        
        consensus_score = sum(1 for o in self.observations if o.others_behaved_same) / n if n > 0 else 0.0
        
        distinctiveness_score = 0.0
        if n > 0:
            behaviors_by_stimulus = {}
            for obs in self.observations:
                if obs.stimulus not in behaviors_by_stimulus:
                    behaviors_by_stimulus[obs.stimulus] = []
                behaviors_by_stimulus[obs.stimulus].append(obs.action)
            
            target_stimulus = self.observations[0].stimulus if self.observations else None
            if target_stimulus and target_stimulus in behaviors_by_stimulus:
                total_occurrences = sum(len(v) for v in behaviors_by_stimulus.values())
                if total_occurrences > 0:
                    distinctiveness_score = len(behaviors_by_stimulus[target_stimulus]) / total_occurrences
        
        consistency_score = 0.0
        if self.observations:
            total_situation_occurrences = sum(o.total_situation_occurrences for o in self.observations)
            total_behaviors = sum(o.previous_occurrences for o in self.observations)
            if total_situation_occurrences > 0:
                consistency_score = total_behaviors / total_situation_occurrences
        
        return CovariationMetrics(
            consensus=consensus_score,
            distinctiveness=distinctiveness_score,
            consistency=consistency_score
        )
    
    def _generate_reasoning(self, metrics: CovariationMetrics) -> list[str]:
        """Generate human-readable reasoning for the analysis."""
        reasoning = []
        
        consensus_label = "HIGH" if metrics.consensus > 0.5 else "LOW"
        reasoning.append(f"Consensus: {consensus_label} ({metrics.consensus:.2%}) - {'Others behave similarly' if metrics.consensus > 0.5 else 'Few others behave this way'}")
        
        distinctiveness_label = "HIGH" if metrics.distinctiveness > 0.5 else "LOW"
        reasoning.append(f"Distinctiveness: {distinctiveness_label} ({metrics.distinctiveness:.2%}) - {'Specific to this stimulus' if metrics.distinctiveness > 0.5 else 'Occurs across multiple stimuli'}")
        
        consistency_label = "HIGH" if metrics.consistency > 0.7 else "LOW"
        reasoning.append(f"Consistency: {consistency_label} ({metrics.consistency:.2%}) - {'Behavior is predictable' if metrics.consistency > 0.7 else 'Behavior varies'}")
        
        return reasoning
    
    def _determine_attribution(self, metrics: CovariationMetrics,
                               consensus_thresh: float,
                               distinctiveness_thresh: float,
                               consistency_thresh: float) -> AttributionType:
        """Determine the attribution type based on covariation metrics."""
        
        low_consensus = metrics.consensus < consensus_thresh
        low_distinctiveness = metrics.distinctiveness < distinctiveness_thresh
        high_consistency = metrics.consistency > consistency_thresh
        
        low_consensus_ext = metrics.consensus > (1 - consensus_thresh)
        high_distinctiveness_ext = metrics.distinctiveness > (1 - distinctiveness_thresh)
        
        if low_consensus and low_distinctiveness and high_consistency:
            return AttributionType.INTERNAL
        
        if low_consensus_ext and high_distinctiveness_ext and high_consistency:
            return AttributionType.EXTERNAL
        
        return AttributionType.AMBIGUOUS
    
    def _calculate_confidence(self, metrics: CovariationMetrics) -> AttributionConfidence:
        """Calculate confidence level based on data quality."""
        data_points = len(self.observations)
        
        if data_points >= 10 and all([metrics.consensus in [0, 1], 
                                       metrics.distinctiveness in [0, 1],
                                       metrics.consistency > 0.9]):
            return AttributionConfidence.HIGH
        elif data_points >= 5:
            return AttributionConfidence.MEDIUM
        else:
            return AttributionConfidence.LOW


class CovariationEngine:
    """
    Main engine for running covariation analysis on behavioral data.
    
    Usage:
        engine = CovariationEngine()
        engine.add_observation(...)
        result = engine.analyze("procrastination")
    """
    
    def __init__(self, consensus_threshold: float = 0.3,
                 distinctiveness_threshold: float = 0.5,
                 consistency_threshold: float = 0.7):
        self.thresholds = {
            "consensus": consensus_threshold,
            "distinctiveness": distinctiveness_threshold,
            "consistency": consistency_threshold
        }
        self.profiles: dict[str, BehaviorProfile] = {}
    
    def add_observation(self, behavior: str, obs: Observation):
        """Add an observation to a behavior profile."""
        if behavior not in self.profiles:
            self.profiles[behavior] = BehaviorProfile(behavior=behavior)
        self.profiles[behavior].add_observation(obs)
    
    def add_observations_from_journey_data(self, journey_data: list[dict]):
        """Add observations from journey/touchpoint data."""
        for journey in journey_data:
            behavior = journey.get("action", journey.get("channel", "unknown"))
            obs = Observation(
                actor=journey.get("actor", "self"),
                action=behavior,
                stimulus=journey.get("context", journey.get("channel", "unknown")),
                context=journey.get("context", ""),
                timestamp=journey.get("timestamp", ""),
                others_behaved_same=False,
                alternative_stimuli_available=True,
                previous_occurrences=1,
                total_situation_occurrences=1
            )
            self.add_observation(behavior, obs)
    
    def analyze_behavior(self, behavior: str) -> CovariationResult:
        """Analyze a specific behavior."""
        if behavior not in self.profiles:
            return CovariationResult(
                attribution_type=AttributionType.AMBIGUOUS,
                confidence=AttributionConfidence.LOW,
                metrics=CovariationMetrics(0.0, 0.0, 0.0),
                reasoning=[f"No observations for behavior: {behavior}"]
            )
        
        return self.profiles[behavior].analyze(
            consensus_thresh=self.thresholds["consensus"],
            distinctiveness_thresh=self.thresholds["distinctiveness"],
            consistency_thresh=self.thresholds["consistency"]
        )
    
    def analyze_all(self) -> dict[str, CovariationResult]:
        """Analyze all tracked behaviors."""
        return {
            behavior: self.analyze_behavior(behavior)
            for behavior in self.profiles
        }
    
    def get_internal_behaviors(self) -> list[str]:
        """Get list of behaviors attributed to internal/dispositional causes."""
        return [
            b for b, r in self.analyze_all().items()
            if r.attribution_type == AttributionType.INTERNAL
        ]
    
    def get_external_behaviors(self) -> list[str]:
        """Get list of behaviors attributed to external/situational causes."""
        return [
            b for b, r in self.analyze_all().items()
            if r.attribution_type == AttributionType.EXTERNAL
        ]
    
    def get_ambiguous_behaviors(self) -> list[str]:
        """Get list of behaviors with ambiguous attribution."""
        return [
            b for b, r in self.analyze_all().items()
            if r.attribution_type == AttributionType.AMBIGUOUS
        ]


def create_covariation_insight(attribution_result: CovariationResult, 
                                behavior: str) -> dict:
    """Generate actionable insight from covariation analysis."""
    
    insight = {
        "behavior": behavior,
        "type": attribution_result.attribution_type.value,
        "confidence": attribution_result.confidence.value,
        "summary": attribution_result.generate_summary(),
        "metrics": attribution_result.metrics.to_dict(),
        "reasoning": attribution_result.reasoning,
        "recommendations": []
    }
    
    if attribution_result.attribution_type == AttributionType.INTERNAL:
        insight["recommendations"] = [
            "This appears to be a core behavioral pattern",
            "Consider building systems around this behavior",
            "If negative: Focus on identity-level change rather than environmental tweaks"
        ]
    elif attribution_result.attribution_type == AttributionType.EXTERNAL:
        insight["recommendations"] = [
            "This behavior is context-driven",
            "Consider modifying the triggering environment",
            "Small environmental changes may yield large behavioral shifts"
        ]
    else:
        insight["recommendations"] = [
            "More data needed for clear attribution",
            "Track additional observations across different contexts",
            "Consider both internal and external factors"
        ]
    
    return insight


def analyze_attribution_with_covariation(
    markov_attribution: dict[str, float],
    shapley_attribution: dict[str, float],
    journey_data: list[dict],
    alpha: float = 0.5
) -> dict:
    """
    Combine Markov-Shapley attribution with Kelley Covariation analysis.
    
    Returns enriched attribution with internal/external classification.
    """
    engine = CovariationEngine()
    engine.add_observations_from_journey_data(journey_data)
    
    covariation_results = engine.analyze_all()
    
    hybrid_attribution = {
        channel: (1 - alpha) * markov_attribution.get(channel, 0) + 
                      alpha * shapley_attribution.get(channel, 0)
        for channel in set(markov_attribution.keys()) | set(shapley_attribution.keys())
    }
    
    enriched_results = {}
    for channel, value in hybrid_attribution.items():
        cov_result = covariation_results.get(channel)
        enriched_results[channel] = {
            "attribution_score": value,
            "attribution_type": cov_result.attribution_type.value if cov_result else "unknown",
            "confidence": cov_result.confidence.value if cov_result else "unknown",
            "covariation_metrics": cov_result.metrics.to_dict() if cov_result else None,
            "insight": create_covariation_insight(cov_result, channel) if cov_result else None
        }
    
    summary = {
        "total_channels": len(hybrid_attribution),
        "internal_attributions": len(engine.get_internal_behaviors()),
        "external_attributions": len(engine.get_external_behaviors()),
        "ambiguous_attributions": len(engine.get_ambiguous_behaviors()),
        "alpha_used": alpha,
        "enriched_results": enriched_results
    }
    
    return summary


if __name__ == "__main__":
    engine = CovariationEngine()
    
    obs1 = Observation(
        actor="self", action="bought_coffee", stimulus="meeting",
        context="had a 9am meeting", timestamp="2024-01-15T08:00:00",
        others_behaved_same=False, alternative_stimuli_available=True,
        previous_occurrences=1, total_situation_occurrences=1
    )
    
    obs2 = Observation(
        actor="self", action="bought_coffee", stimulus="meeting",
        context="had a 9am meeting", timestamp="2024-01-22T08:00:00",
        others_behaved_same=False, alternative_stimuli_available=True,
        previous_occurrences=2, total_situation_occurrences=2
    )
    
    obs3 = Observation(
        actor="self", action="bought_coffee", stimulus="no_meeting",
        context="just felt like it", timestamp="2024-01-29T09:00:00",
        others_behaved_same=False, alternative_stimuli_available=True,
        previous_occurrences=3, total_situation_occurrences=1
    )
    
    engine.add_observation("coffee_buying", obs1)
    engine.add_observation("coffee_buying", obs2)
    engine.add_observation("coffee_buying", obs3)
    
    result = engine.analyze_behavior("coffee_buying")
    print(result.to_dict())
