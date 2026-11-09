"""
Pydantic models for detected dark patterns.
"""

from pydantic import BaseModel, Field


class DetectedPattern(BaseModel):
    """Represents a single dark pattern detected on a page."""

    category: str = Field(
        ...,
        description="Dark pattern category, e.g. 'Confirm Shaming', 'Fake Urgency'",
    )
    severity: str = Field(
        ...,
        description="Severity level: Low, Medium, High, or Critical",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score from 0.0 to 1.0",
    )
    evidence: str = Field(
        ...,
        description="The actual text or element that was flagged",
    )
    explanation: str = Field(
        ...,
        description="Human-readable explanation of why this is a dark pattern",
    )
    recommendation: str = Field(
        ...,
        description="Actionable recommendation for the user",
    )
    detection_method: str = Field(
        ...,
        description="Detection method used: 'rule', 'nlp', or 'dom'",
    )
    rule_id: str | None = Field(
        default=None,
        description="Rule identifier if detected via rule-based engine",
    )
