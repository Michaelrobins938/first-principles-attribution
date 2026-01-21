"""
Psychographic Weighting Engine

This module applies behavioral context to attribution weights, implementing
the PRD's "secret weapon" - psychographic analysis that extracts motivation,
intent, and emotional context to dynamically adjust attribution weights.
"""

from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import math


class PsychographicWeighting:
    """
    Apply behavioral context to attribution weights based on psychographic factors.

    This implements contextual multipliers that enhance base attribution values
    based on user intent level, platform context, and emotional state.
    """

    # Context-based weight multipliers
    CONTEXT_WEIGHTS = {
        "high_intent": 1.5,           # Deep engagement, clear purpose
        "medium_intent": 1.0,         # Normal browsing behavior
        "low_intent": 0.7,            # Passive consumption
        "mobile_discovery": 1.2,       # Mobile context (discovery phase)
        "desktop_execution": 1.3,      # Desktop context (execution phase)
        "emotional_positive": 1.1,     # Positive sentiment
        "emotional_negative": 0.9,     # Negative sentiment
        "repeat_interaction": 1.25,    # Multiple touchpoints with same channel
        "first_interaction": 0.8,      # Initial discovery
        "research_phase": 1.15,        # Exploratory behavior
        "decision_phase": 1.4,         # Near-conversion behavior
    }

    # Channel affinity patterns
    CHANNEL_AFFINITIES = {
        "Google_Search": ["high_intent", "decision_phase", "research_phase"],
        "Facebook_Social": ["low_intent", "mobile_discovery", "repeat_interaction"],
        "AI_Assistant": ["high_intent", "decision_phase", "research_phase"],
        "YouTube": ["medium_intent", "research_phase", "mobile_discovery"],
        "Snapchat_Messaging": ["low_intent", "mobile_discovery", "first_interaction"],
        "Instagram_Social": ["low_intent", "mobile_discovery", "repeat_interaction"],
        "Google_YouTube": ["medium_intent", "research_phase", "mobile_discovery"],
        "Apple_Mobile": ["medium_intent", "execution_phase", "repeat_interaction"],
        "Android_Mobile": ["medium_intent", "execution_phase", "repeat_interaction"],
        "Facebook_Messages": ["high_intent", "desktop_execution", "repeat_interaction"],
    }

    def __init__(self, journeys: List[Dict] = None):
        """
        Initialize psychographic weighting engine.

        Args:
            journeys: Optional list of journey data for learning patterns
        """
        self.journeys = journeys or []
        self.learned_weights = self._learn_from_journeys() if journeys else {}

    def apply_weights(self, channel: str, context: Dict) -> float:
        """
        Apply psychographic multipliers to a channel based on context.

        Args:
            channel: Name of the channel
            context: Context dictionary with behavioral attributes
                    - intent_level: 'high', 'medium', 'low'
                    - device: 'mobile', 'desktop'
                    - phase: 'discovery', 'research', 'decision', 'execution'
                    - sentiment: 'positive', 'negative', 'neutral'
                    - interaction_count: number of prior interactions
                    - dwell_time_seconds: time spent on content

        Returns:
            float: Weighted multiplier (typically 0.5 to 2.0)
        """
        base_weight = 1.0

        # Apply context multipliers
        intent_level = context.get("intent_level", "medium")
        if f"{intent_level}_intent" in self.CONTEXT_WEIGHTS:
            base_weight *= self.CONTEXT_WEIGHTS[f"{intent_level}_intent"]

        # Device context
        device = context.get("device", "desktop")
        if device == "mobile":
            base_weight *= self.CONTEXT_WEIGHTS.get("mobile_discovery", 1.0)
        elif device == "desktop":
            base_weight *= self.CONTEXT_WEIGHTS.get("desktop_execution", 1.0)

        # Journey phase
        phase = context.get("phase", "research")
        phase_key = f"{phase}_phase"
        if phase_key in self.CONTEXT_WEIGHTS:
            base_weight *= self.CONTEXT_WEIGHTS[phase_key]

        # Emotional context
        sentiment = context.get("sentiment", "neutral")
        if sentiment == "positive":
            base_weight *= self.CONTEXT_WEIGHTS.get("emotional_positive", 1.0)
        elif sentiment == "negative":
            base_weight *= self.CONTEXT_WEIGHTS.get("emotional_negative", 1.0)

        # Interaction history
        interaction_count = context.get("interaction_count", 1)
        if interaction_count > 1:
            # Each additional interaction increases weight slightly
            repeat_multiplier = 1.0 + (0.15 * min(interaction_count - 1, 3))
            base_weight *= repeat_multiplier
        elif interaction_count == 0:
            base_weight *= self.CONTEXT_WEIGHTS.get("first_interaction", 1.0)

        # Dwell time adjustment (logarithmic scale)
        dwell_seconds = context.get("dwell_time_seconds", 0)
        if dwell_seconds > 0:
            dwell_multiplier = 1.0 + (0.1 * math.log(dwell_seconds + 1))
            base_weight *= dwell_multiplier

        # Channel-specific affinity boost
        if channel in self.CHANNEL_AFFINITIES:
            affinity_contexts = self.CHANNEL_AFFINITIES[channel]
            matching_affinities = sum(
                1 for context_key in affinity_contexts
                if self._matches_affinity_context(context, context_key)
            )
            if matching_affinities > 0:
                base_weight *= (1.0 + (0.1 * matching_affinities))

        # Apply learned weights if available
        if channel in self.learned_weights:
            base_weight *= self.learned_weights[channel]

        return base_weight

    def _matches_affinity_context(self, context: Dict, affinity_key: str) -> bool:
        """Check if context matches an affinity key."""
        if "intent" in affinity_key:
            intent_level = context.get("intent_level", "medium")
            return f"{intent_level}_intent" == affinity_key

        if "phase" in affinity_key:
            phase = context.get("phase", "research")
            return f"{phase}_phase" == affinity_key

        if "mobile" in affinity_key:
            return context.get("device") == "mobile"

        if "desktop" in affinity_key:
            return context.get("device") == "desktop"

        if "interaction" in affinity_key:
            if "repeat" in affinity_key:
                return context.get("interaction_count", 1) > 1
            elif "first" in affinity_key:
                return context.get("interaction_count", 1) <= 1

        return False

    def extract_psychographic_profile(self, journey_data: Dict) -> Dict:
        """
        Extract psychographic profile from journey data.

        Returns dictionary with:
        - motivations: dict of motivation types and scores
        - fears: list of identified fears/avoidances
        - desires: list of aspirational goals
        - behavioral_rhythm: activity patterns
        - personality_traits: inferred traits
        """
        profile = {
            "motivations": self._extract_motivations(journey_data),
            "fears": self._extract_fears(journey_data),
            "desires": self._extract_desires(journey_data),
            "behavioral_rhythm": self._analyze_temporal_patterns(journey_data),
            "personality_traits": self._infer_personality_traits(journey_data),
            "buying_psychology": self._analyze_buying_behavior(journey_data)
        }
        return profile

    def _extract_motivations(self, journey_data: Dict) -> Dict[str, float]:
        """Extract motivation scores from journey data."""
        motivations = {
            "growth": 0.0,
            "relief": 0.0,
            "optimization": 0.0,
            "social_connection": 0.0,
            "entertainment": 0.0
        }

        # Analyze channels for motivation signals
        channels = journey_data.get("path", [])
        for tp in channels:
            channel = tp.get("channel", "")

            if "Search" in channel:
                motivations["growth"] += 0.3
                motivations["relief"] += 0.2
            elif "YouTube" in channel or "Social" in channel:
                motivations["entertainment"] += 0.25
                motivations["social_connection"] += 0.15
            elif "AI_Assistant" in channel or "ChatGPT" in channel:
                motivations["growth"] += 0.4
                motivations["relief"] += 0.3
            elif "Message" in channel:
                motivations["social_connection"] += 0.3

        # Normalize scores
        total = sum(motivations.values())
        if total > 0:
            motivations = {k: v/total for k, v in motivations.items()}

        return motivations

    def _extract_fears(self, journey_data: Dict) -> List[str]:
        """Extract fear/avoidance patterns from journey data."""
        fears = []

        # If many failed conversions, suggest uncertainty fears
        if journey_data.get("conversion") == False:
            fears.append("decision_uncertainty")
            fears.append("missing_information")

        # Repeated searches suggest problem-solving fears
        if "Search" in str(journey_data.get("path", [])):
            fears.append("incompleteness")

        return list(set(fears))

    def _extract_desires(self, journey_data: Dict) -> List[str]:
        """Extract aspirational desires from journey data."""
        desires = []

        channels = journey_data.get("path", [])
        for tp in channels:
            channel = tp.get("channel", "")

            if "Search" in channel:
                desires.append("self_improvement")
            elif "social" in channel.lower():
                desires.append("recognition")
                desires.append("connection")
            elif "AI" in channel:
                desires.append("efficiency")
                desires.append("mastery")

        return list(set(desires))

    def _analyze_temporal_patterns(self, journey_data: Dict) -> Dict:
        """Analyze temporal/behavioral rhythm patterns."""
        path = journey_data.get("path", [])

        if not path:
            return {"chronotype": "unknown", "activity_density": "low"}

        # Simple analysis based on path length
        num_touchpoints = len(path)

        rhythm = {
            "activity_density": "high" if num_touchpoints > 5 else "medium" if num_touchpoints > 2 else "low",
            "journey_intensity": "intense" if num_touchpoints > 8 else "moderate" if num_touchpoints > 4 else "exploratory",
            "engagement_level": "deep" if num_touchpoints > 5 else "medium" if num_touchpoints > 2 else "light"
        }

        return rhythm

    def _infer_personality_traits(self, journey_data: Dict) -> List[str]:
        """Infer personality traits from journey behavior."""
        traits = []

        channels = journey_data.get("path", [])
        channel_diversity = len(set(tp.get("channel") for tp in channels))

        # Diversity suggests openness/curiosity
        if channel_diversity > 3:
            traits.append("curious")
            traits.append("exploratory")

        # Search behavior suggests analytical nature
        if any("Search" in tp.get("channel", "") for tp in channels):
            traits.append("analytical")
            traits.append("research_oriented")

        # Social channels suggest sociability
        if any("Social" in tp.get("channel", "") or "Message" in tp.get("channel", "") for tp in channels):
            traits.append("social")
            traits.append("collaborative")

        return traits

    def _analyze_buying_behavior(self, journey_data: Dict) -> Dict:
        """Analyze buying psychology from journey data."""
        path_length = len(journey_data.get("path", []))
        is_conversion = journey_data.get("conversion", False)

        return {
            "buyer_type": "deliberate" if path_length > 5 else "impulsive" if path_length < 2 else "normal",
            "decision_quality": "thorough" if path_length > 4 else "adequate" if path_length > 1 else "quick",
            "conversion_likelihood": "high" if is_conversion else "low",
            "preferred_channels": self._identify_preferred_channels(path_length)
        }

    def _identify_preferred_channels(self, path_length: int) -> str:
        """Identify preferred channel type based on path characteristics."""
        if path_length <= 1:
            return "direct"
        elif path_length <= 3:
            return "limited_research"
        else:
            return "thorough_research"

    def _learn_from_journeys(self) -> Dict[str, float]:
        """Learn channel weights from journey data."""
        learned_weights = defaultdict(list)

        for journey in self.journeys:
            if journey.get("conversion"):
                path = journey.get("path", [])
                for tp in path:
                    channel = tp.get("channel", "")
                    # Conversions get boosted
                    learned_weights[channel].append(1.1)
            else:
                path = journey.get("path", [])
                for tp in path:
                    channel = tp.get("channel", "")
                    # Non-conversions get reduced
                    learned_weights[channel].append(0.95)

        # Average learned weights
        averaged = {}
        for channel, weights in learned_weights.items():
            averaged[channel] = sum(weights) / len(weights) if weights else 1.0

        return averaged

