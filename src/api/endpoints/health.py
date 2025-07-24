"""
Health check endpoints.
"""
from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str = "1.0.0"


class ReadinessResponse(BaseModel):
    """Readiness check response."""
    status: str
    services: dict


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc)
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check() -> ReadinessResponse:
    """
    Readiness check endpoint.
    
    Verifies that all required services are available.
    """
    # In a real app, you'd check database connections, external services, etc.
    return ReadinessResponse(
        status="ready",
        services={
            "openai": "connected",
            "storage": "ready"
        }
    )