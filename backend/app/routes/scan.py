"""
POST /api/scan endpoint.
Receives website DOM, text, and structural data, runs detection engine,
persists results (MongoDB with in-memory fallback), and returns analysis.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.scan import ScanRequest, ScanResponse
from app.detection.engine import DetectionEngine
from app.database import get_database

router = APIRouter(prefix="/api/scan", tags=["Scan"])
detection_engine = DetectionEngine()

# In-memory storage cache as fallback when MongoDB is unavailable
IN_MEMORY_SCANS: list[dict] = []


@router.post("", response_model=ScanResponse, status_code=status.HTTP_200_OK)
async def scan_page(scan_request: ScanRequest) -> ScanResponse:
    """Analyze a webpage payload for dark patterns."""
    if not scan_request.url:
        scan_request.url = scan_request.meta.url or "https://unknown-website.com"

    # Execute full detection pipeline
    result = detection_engine.scan(scan_request)

    # Persist scan result
    scan_doc = result.model_dump()
    # Serialize datetime to ISO string for storage
    scan_doc["scanned_at_iso"] = result.scanned_at.isoformat()

    db = get_database()
    if db is not None:
        try:
            await db.scans.insert_one(scan_doc)
        except Exception as e:
            # Fall back to in-memory storage
            IN_MEMORY_SCANS.insert(0, scan_doc)
    else:
        IN_MEMORY_SCANS.insert(0, scan_doc)
        # Cap in-memory size
        if len(IN_MEMORY_SCANS) > 200:
            IN_MEMORY_SCANS.pop()

    return result

