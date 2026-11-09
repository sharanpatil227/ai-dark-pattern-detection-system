"""
Pydantic models for reports and dashboard statistics.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from app.models.pattern import DetectedPattern


class ReportSummary(BaseModel):
    """Summary of a scan report for list views."""

    scan_id: str
    url: str
    risk_score: int
    risk_level: str
    total_patterns: int
    scanned_at: datetime


class ReportDetail(BaseModel):
    """Full detail of a scan report."""

    scan_id: str
    url: str
    risk_score: int
    risk_level: str
    total_patterns: int
    patterns: list[DetectedPattern] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    scanned_at: datetime


class PaginatedReports(BaseModel):
    """Paginated list of report summaries."""

    reports: list[ReportSummary] = Field(default_factory=list)
    total: int = Field(default=0)
    page: int = Field(default=1)
    page_size: int = Field(default=20)
    total_pages: int = Field(default=0)


class CategoryCount(BaseModel):
    """Count of patterns per category."""

    category: str
    count: int


class ScanOverTime(BaseModel):
    """Number of scans per day."""

    date: str
    count: int


class DashboardStats(BaseModel):
    """Aggregated statistics for the dashboard."""

    total_scans: int = Field(default=0)
    total_patterns_found: int = Field(default=0)
    average_risk_score: float = Field(default=0.0)
    high_risk_count: int = Field(default=0)
    top_patterns: list[CategoryCount] = Field(default_factory=list)
    category_distribution: list[CategoryCount] = Field(default_factory=list)
    scans_over_time: list[ScanOverTime] = Field(default_factory=list)
    risk_level_distribution: dict[str, int] = Field(default_factory=dict)
