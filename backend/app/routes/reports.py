"""
GET /api/reports endpoints.
Provides historical reports and detailed analysis lookups.
"""

from fastapi import APIRouter, HTTPException, Query, status
from app.models.report import ReportSummary, ReportDetail, PaginatedReports
from app.database import get_database
from app.routes.scan import IN_MEMORY_SCANS

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("", response_model=PaginatedReports)
async def list_reports(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    url_filter: str | None = Query(default=None, description="Filter by partial URL"),
) -> PaginatedReports:
    """Retrieve paginated scan reports."""
    db = get_database()
    reports_list: list[ReportSummary] = []
    total = 0

    if db is not None:
        try:
            query = {}
            if url_filter:
                query["url"] = {"$regex": url_filter, "$options": "i"}

            total = await db.scans.count_documents(query)
            cursor = (
                db.scans.find(query, {"_id": 0})
                .sort("scanned_at", -1)
                .skip((page - 1) * limit)
                .limit(limit)
            )
            async for doc in cursor:
                reports_list.append(
                    ReportSummary(
                        scan_id=doc["scan_id"],
                        url=doc["url"],
                        risk_score=doc["risk_score"],
                        risk_level=doc["risk_level"],
                        total_patterns=doc["total_patterns"],
                        scanned_at=doc["scanned_at"],
                    )
                )
        except Exception:
            db = None  # Fall back to in-memory

    if db is None:
        filtered = IN_MEMORY_SCANS
        if url_filter:
            filtered = [s for s in filtered if url_filter.lower() in s["url"].lower()]

        total = len(filtered)
        start = (page - 1) * limit
        end = start + limit
        paged = filtered[start:end]

        for doc in paged:
            reports_list.append(
                ReportSummary(
                    scan_id=doc["scan_id"],
                    url=doc["url"],
                    risk_score=doc["risk_score"],
                    risk_level=doc["risk_level"],
                    total_patterns=doc["total_patterns"],
                    scanned_at=doc["scanned_at"],
                )
            )

    total_pages = (total + limit - 1) // limit if total > 0 else 0

    return PaginatedReports(
        reports=reports_list,
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get("/{scan_id}", response_model=ReportDetail)
async def get_report_detail(scan_id: str) -> ReportDetail:
    """Fetch full detail for an individual scan report."""
    db = get_database()
    if db is not None:
        try:
            doc = await db.scans.find_one({"scan_id": scan_id}, {"_id": 0})
            if doc:
                return ReportDetail(**doc)
        except Exception:
            pass

    # Search in-memory
    for doc in IN_MEMORY_SCANS:
        if doc.get("scan_id") == scan_id:
            return ReportDetail(**doc)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

