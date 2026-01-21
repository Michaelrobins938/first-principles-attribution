from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class TouchPoint(BaseModel):
    channel: str
    timestamp: datetime
    context: Optional[str] = None

class Journey(BaseModel):
    journey_id: str
    path: List[TouchPoint]
    conversion: bool = False
    conversion_value: float = 0.0
    num_touchpoints: int = 0
    duration_hours: float = 0.0

class AttributionRequest(BaseModel):
    journeys: List[Journey]

class ChannelAttribution(BaseModel):
    channel: str
    markov_contribution: float
    shapley_value: float
    hybrid_weighted: float
    confidence_interval: tuple[float, float]

class AttributionResponse(BaseModel):
    status: str
    processing_time_ms: float
    total_journeys: int
    total_conversions: int
    unique_channels: int
    channel_attributions: Dict[str, float]
    alpha_used: float
    confidence_intervals: Dict[str, Dict[str, float]]
