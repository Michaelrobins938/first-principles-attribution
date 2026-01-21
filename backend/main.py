"""
Attribution Mind Map - FastAPI Backend

This module provides the main FastAPI application for the attribution analysis service.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config import settings
from backend.api.router import router as attribution_router
from backend.api.routers.behavioral import router as behavioral_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    yield


app = FastAPI(
    title=settings.app_name,
    description="Attribution Mind Map - Behavioral Intelligence & Attribution Engine",
    version="2.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(attribution_router, prefix="/api/v1/attribution", tags=["Attribution"])
app.include_router(behavioral_router, prefix="/api/v1/behavioral", tags=["Behavioral"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/attribution/health"
    }


@app.get("/api/v1/health")
async def health():
    """Overall health check."""
    return {"status": "healthy", "service": "attribution-mind-map-api"}


@app.post("/api/v1/debug/upload")
async def debug_upload(file: UploadFile = File(...)):
    """Debug endpoint for file upload."""
    try:
        content = await file.read()
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "content_length": len(content),
            "content_preview": content[:200].decode('utf-8', errors='replace')
        }
    except Exception as e:
        return {"error": str(e)}


def run():
    """Run the API server."""
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )


if __name__ == "__main__":
    run()
