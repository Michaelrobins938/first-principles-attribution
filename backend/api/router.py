from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from models.attribution import AttributionRequest
from engines.attribution.engine import AttributionEngine

router = APIRouter()

@router.post("/analyze")
async def analyze_attribution(request: AttributionRequest) -> Dict[str, Any]:
    try:
        engine = AttributionEngine(request.journeys)
        result = engine.run_analysis(alpha=0.5)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    return {"status": "healthy", "service": "attribution-api"}
