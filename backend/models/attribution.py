from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TouchPoint(BaseModel):
    channel: str
    timestamp: datetime
    context: Optional[str] = None


class Journey(BaseModel):
    journey_id: str
    path: list[TouchPoint]
    conversion: bool
    conversion_value: float = 0.0
    num_touchpoints: int
    duration_hours: float


class AttributionRequest(BaseModel):
    journeys: list[Journey]
    alpha: float = Field(default=0.5, ge=0.0, le=1.0, description="Weight for Markov (1-alpha) vs Shapley (alpha)")
    include_uncertainty: bool = True
    filter_channels: Optional[list[str]] = None


class ChannelMetrics(BaseModel):
    channel: str
    markov_contribution: float = 0.0
    shapley_value: float = 0.0
    hybrid_weighted: float = 0.0
    markov_confidence_low: float = 0.0
    markov_confidence_high: float = 0.0
    touchpoint_count: int = 0
    conversion_rate: float = 0.0
    avg_position: float = 0.0


class ChannelAttribution(BaseModel):
    channel: str
    total_attribution: float
    percentage: float
    touchpoints: int
    conversion_rate: float


class MarkovResult(BaseModel):
    channel_attributions: dict[str, float]
    transition_matrix: dict[str, dict[str, float]]
    removal_effects: dict[str, float]
    total_conversions: int
    confidence_interval: dict[str, dict[str, float]]


class ShapleyResult(BaseModel):
    channel_values: dict[str, float]
    marginal_contributions: dict[str, list[float]]
    convergence: bool
    iterations: int


class HybridResult(BaseModel):
    channel_attributions: dict[str, float]
    alpha_used: float
    markov_weight: float
    shapley_weight: float
    confidence_intervals: dict[str, dict[str, float]]


class AttributionResponse(BaseModel):
    status: str
    processing_time_ms: float
    total_journeys: int
    total_conversions: int
    unique_channels: int
    markov_result: Optional[MarkovResult] = None
    shapley_result: Optional[ShapleyResult] = None
    hybrid_result: Optional[HybridResult] = None
    channel_metrics: list[ChannelMetrics]
    channels_summary: dict[str, int]
