"""
GET /api/dashboard/stats endpoint.
Aggregates scan history and risk analytics for the frontend dashboard.
"""

from collections import Counter, defaultdict
from datetime import datetime
from fastapi import APIRouter
from app.models.report import DashboardStats, CategoryCount, ScanOverTime
from app.database import get_database
from app.routes.scan import IN_MEMORY_SCANS

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats() -> DashboardStats:
    """Compute aggregated dashboard analytics."""
    db = get_database()
    scans_data = []

    if db is not None:
        try:
            cursor = db.scans.find({}, {"_id": 0})
            async for doc in cursor:
                scans_data.append(doc)
        except Exception:
            scans_data = list(IN_MEMORY_SCANS)
    else:
        scans_data = list(IN_MEMORY_SCANS)

    if not scans_data:
        # Return sensible empty state
        return DashboardStats(
            total_scans=0,
            total_patterns_found=0,
            average_risk_score=0.0,
            high_risk_count=0,
            top_patterns=[],
            category_distribution=[],
            scans_over_time=[],
            risk_level_distribution={"Low": 0, "Medium": 0, "High": 0, "Critical": 0},
        )

    total_scans = len(scans_data)
    total_patterns = sum(s.get("total_patterns", 0) for s in scans_data)
    avg_score = round(sum(s.get("risk_score", 0) for s in scans_data) / total_scans, 1)

    high_risk_count = sum(
        1 for s in scans_data if s.get("risk_level") in ["High", "Critical"]
    )

    # Category distribution
    cat_counter = Counter()
    for s in scans_data:
        for p in s.get("patterns", []):
            cat = p.get("category")
            if cat:
                cat_counter[cat] += 1

    category_distribution = [
        CategoryCount(category=cat, count=cnt)
        for cat, cnt in cat_counter.most_common()
    ]
    top_patterns = category_distribution[:5]

    # Scans over time (by date)
    date_counter = defaultdict(int)
    for s in scans_data:
        st = s.get("scanned_at")
        if isinstance(st, datetime):
            date_str = st.strftime("%Y-%m-%d")
        elif isinstance(st, str):
            date_str = st[:10]
        else:
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
        date_counter[date_str] += 1

    sorted_dates = sorted(date_counter.items())
    scans_over_time = [
        ScanOverTime(date=d, count=c) for d, c in sorted_dates[-30:]
    ]

    # Risk level counts
    level_counts = Counter(s.get("risk_level", "Low") for s in scans_data)
    risk_level_distribution = {
        "Low": level_counts["Low"],
        "Medium": level_counts["Medium"],
        "High": level_counts["High"],
        "Critical": level_counts["Critical"],
    }

    return DashboardStats(
        total_scans=total_scans,
        total_patterns_found=total_patterns,
        average_risk_score=avg_score,
        high_risk_count=high_risk_count,
        top_patterns=top_patterns,
        category_distribution=category_distribution,
        scans_over_time=scans_over_time,
        risk_level_distribution=risk_level_distribution,
    )

