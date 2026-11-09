"""
Health check endpoint.
Reports system status, database connectivity, and ML model loading state.
"""

from fastapi import APIRouter
from app.database import is_db_connected
from app.routes.scan import detection_engine

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("")
async def health_check():
    """Returns application health and operational statuses."""
    db_ok = await is_db_connected()
    ml_ok = detection_engine.nlp_engine.is_loaded

    return {
        "status": "healthy",
        "service": "AI-Powered Dark Pattern Detection System",
        "database_connected": db_ok,
        "ml_model_loaded": ml_ok,
        "version": "1.0.0",
    }

