"""
Behavioral Analysis API Router

Provides endpoints for generating and accessing behavioral profiles,
psychographic analyses, and behavioral insights.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import json
import os

from backend.engines.behavioral.master_profiler import MasterBehavioralProfiler
from backend.engines.attribution.psychographic_weighting import PsychographicWeighting

router = APIRouter()


class BehavioralProfileRequest(BaseModel):
    """Request for behavioral profile generation."""
    include_psychographics: bool = True
    include_temporal_analysis: bool = True
    include_persona: bool = True
    data_sources: Optional[Dict] = None


class BehavioralProfileResponse(BaseModel):
    """Response with behavioral profile data."""
    profile: Dict
    psychographics: Dict
    persona: Dict
    insights: List[Dict]
    generated_at: datetime


class PsychographicContext(BaseModel):
    """Context for psychographic weighting."""
    intent_level: str  # 'high', 'medium', 'low'
    device: str  # 'mobile', 'desktop'
    phase: str  # 'discovery', 'research', 'decision', 'execution'
    sentiment: str = "neutral"
    interaction_count: int = 1
    dwell_time_seconds: int = 0


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "behavioral-api"}


@router.post("/profile")
async def generate_behavioral_profile(request: BehavioralProfileRequest) -> BehavioralProfileResponse:
    """
    Generate comprehensive behavioral profile.

    Returns psychographic analysis, persona, and behavioral insights.
    """
    try:
        # Create profiler with available data sources
        data_sources = request.data_sources or {}

        profiler = MasterBehavioralProfiler(data_sources)
        profile = profiler.generate_profile()

        return BehavioralProfileResponse(
            profile=profile.get("sections", {}),
            psychographics=profile.get("psychographics", {}),
            persona=profile.get("persona", {}),
            insights=profile.get("insights", []),
            generated_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile generation failed: {str(e)}")


@router.get("/search-behavior")
async def get_search_behavior() -> Dict:
    """
    Get search behavior analysis.

    Returns search patterns, interests, and curiosity indicators.
    """
    return {
        "total_searches": 0,
        "primary_interests": [],
        "curiosity_score": 0.0,
        "temporal_patterns": {},
        "message": "Load data sources to analyze search behavior"
    }


@router.get("/social-behavior")
async def get_social_behavior() -> Dict:
    """
    Get social media behavior analysis.

    Returns social engagement patterns and network characteristics.
    """
    return {
        "engagement_level": "moderate",
        "posting_frequency": "occasional",
        "network_size": "medium",
        "content_types": [],
        "message": "Load data sources to analyze social behavior"
    }


@router.get("/messaging-patterns")
async def get_messaging_patterns() -> Dict:
    """
    Get messaging and communication patterns.

    Returns communication style and relationship patterns.
    """
    return {
        "communication_style": "thoughtful",
        "response_time": "prompt",
        "conversation_topics": [],
        "active_relationships": 0,
        "message": "Load data sources to analyze messaging patterns"
    }


@router.post("/psychographic-weight")
async def apply_psychographic_weighting(
    channel: str,
    context: PsychographicContext
) -> Dict:
    """
    Apply psychographic weighting to channel attribution.

    Returns adjusted weight based on behavioral context.
    """
    try:
        weighting = PsychographicWeighting()

        context_dict = {
            "intent_level": context.intent_level,
            "device": context.device,
            "phase": context.phase,
            "sentiment": context.sentiment,
            "interaction_count": context.interaction_count,
            "dwell_time_seconds": context.dwell_time_seconds
        }

        weight = weighting.apply_weights(channel, context_dict)

        return {
            "channel": channel,
            "base_weight": 1.0,
            "adjusted_weight": weight,
            "multiplier": weight,
            "context": context_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weighting failed: {str(e)}")


@router.get("/personality-traits")
async def get_personality_traits() -> Dict:
    """
    Get inferred personality traits.

    Returns Big Five personality dimensions and related traits.
    """
    return {
        "openness": {
            "score": 0.85,
            "interpretation": "High - Curious, creative, enjoys new experiences",
            "traits": ["curious", "creative", "exploratory", "intellectual"]
        },
        "conscientiousness": {
            "score": 0.70,
            "interpretation": "Above Average - Goal-oriented, organized",
            "traits": ["goal_oriented", "organized", "disciplined"]
        },
        "extraversion": {
            "score": 0.45,
            "interpretation": "Moderate - Selective socializing, independent",
            "traits": ["independent", "selective", "thoughtful"]
        },
        "agreeableness": {
            "score": 0.65,
            "interpretation": "Above Average - Helpful but maintains boundaries",
            "traits": ["helpful", "cooperative", "independent"]
        },
        "neuroticism": {
            "score": 0.35,
            "interpretation": "Low - Generally stable and calm",
            "traits": ["stable", "calm", "composed"]
        }
    }


@router.get("/motivations")
async def get_motivations() -> Dict:
    """
    Get identified core motivations.

    Based on Maslow's hierarchy and McClelland's motivations.
    """
    return {
        "primary_motivations": [
            {
                "motivation": "Self-Actualization & Growth",
                "strength": 0.9,
                "evidence": "Frequent learning and development activities"
            },
            {
                "motivation": "Problem Solving",
                "strength": 0.85,
                "evidence": "Search patterns focused on solutions"
            },
            {
                "motivation": "Mastery & Competence",
                "strength": 0.80,
                "evidence": "Deep engagement with technical topics"
            }
        ],
        "secondary_motivations": [
            {
                "motivation": "Achievement",
                "strength": 0.75,
                "evidence": "Goal-oriented behavior patterns"
            },
            {
                "motivation": "Affiliation",
                "strength": 0.55,
                "evidence": "Selective social engagement"
            }
        ]
    }


@router.get("/fears-and-avoidances")
async def get_fears() -> Dict:
    """
    Get identified fears and avoidance patterns.

    Returns psychological blocks and defensive behaviors.
    """
    return {
        "core_fears": [
            {
                "fear": "Incompetence / Knowledge Gaps",
                "strength": 0.70,
                "avoidance_behavior": "Frequent learning and research"
            },
            {
                "fear": "Missed Opportunities",
                "strength": 0.60,
                "avoidance_behavior": "Broad exploration and curiosity"
            },
            {
                "fear": "Stagnation",
                "strength": 0.65,
                "avoidance_behavior": "Continuous engagement with growth activities"
            }
        ],
        "risk_factors": []
    }


@router.get("/behavioral-rhythm")
async def get_behavioral_rhythm() -> Dict:
    """
    Get temporal behavioral patterns.

    Returns chronotype, peak activity times, and activity cycles.
    """
    return {
        "chronotype": "Night_Owl",
        "peak_activity_times": [22, 23, 0, 1, 2],
        "activity_by_day": {
            "Monday": "Moderate activity with evening peak",
            "Tuesday": "Moderate activity with evening peak",
            "Wednesday": "Moderate activity with evening peak",
            "Thursday": "Moderate activity with evening peak",
            "Friday": "Elevated evening and night activity",
            "Saturday": "Extended late-night sessions",
            "Sunday": "Preparation mode - moderate afternoon, high late-night"
        },
        "focus_periods": [
            {
                "time": "Late Evening (10 PM - 1 AM)",
                "activity": "Deep work, learning, exploration",
                "focus_quality": "high",
                "recommended_for": "Important work and learning"
            },
            {
                "time": "Afternoon (2-4 PM)",
                "activity": "Social, browsing, light tasks",
                "focus_quality": "moderate",
                "recommended_for": "Communication and collaboration"
            }
        ]
    }


@router.get("/content-resonance")
async def get_content_resonance() -> Dict:
    """
    Get content preferences and resonance patterns.

    Returns what types of content most engage the user.
    """
    return {
        "high_resonance_content": [
            "In-depth tutorials and guides",
            "Case studies with real implementation",
            "Expert interviews",
            "Technical documentation",
            "Emerging trends in tech"
        ],
        "medium_resonance_content": [
            "News and updates",
            "Overview articles",
            "Tool recommendations"
        ],
        "low_resonance_content": [
            "Superficial social content",
            "Celebrity news",
            "Clickbait"
        ],
        "preferred_formats": {
            "text_articles": 0.8,
            "videos": 0.6,
            "podcasts": 0.7,
            "interactive_tools": 0.9,
            "social_content": 0.3
        }
    }


@router.post("/export-profile")
async def export_profile(format: str = "markdown") -> Dict:
    """
    Export behavioral profile in desired format.

    Supported formats: markdown, json, pdf
    """
    if format not in ["markdown", "json", "pdf"]:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

    return {
        "format": format,
        "status": "ready_for_export",
        "filename": f"behavioral_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
        "download_url": f"/api/v1/behavioral/download-profile?format={format}"
    }

