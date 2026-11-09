"""
Pydantic models for scan requests and responses.
"""

from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from app.models.pattern import DetectedPattern


class ButtonInfo(BaseModel):
    """Information about a button element on the page."""

    text: str = Field(default="", description="Visible text of the button")
    type: str = Field(default="button", description="Button type attribute")
    classes: str = Field(default="", description="CSS class names on the button")
    is_visible: bool = Field(default=True, description="Whether the button is visible")
    width: int = Field(default=0, description="Button width in pixels")
    height: int = Field(default=0, description="Button height in pixels")
    font_size: str = Field(default="", description="Font size of button text")
    background_color: str = Field(default="", description="Background color of button")
    color: str = Field(default="", description="Text color of button")
    nearby_text: str = Field(default="", description="Text near the button in the DOM")


class LinkInfo(BaseModel):
    """Information about a link element on the page."""

    text: str = Field(default="", description="Visible text of the link")
    href: str = Field(default="", description="URL the link points to")
    classes: str = Field(default="", description="CSS class names")
    is_visible: bool = Field(default=True, description="Whether the link is visible")
    font_size: str = Field(default="", description="Font size")
    color: str = Field(default="", description="Text color")
    nearby_text: str = Field(default="", description="Text near the link")


class CheckboxInfo(BaseModel):
    """Information about a checkbox element on the page."""

    label: str = Field(default="", description="Label text for the checkbox")
    is_checked: bool = Field(default=False, description="Whether checked by default")
    is_visible: bool = Field(default=True, description="Whether the checkbox is visible")
    name: str = Field(default="", description="Name attribute of the checkbox")
    nearby_text: str = Field(default="", description="Text near the checkbox")


class FormInfo(BaseModel):
    """Information about a form element on the page."""

    action: str = Field(default="", description="Form action URL")
    method: str = Field(default="", description="Form HTTP method")
    fields: list[str] = Field(default_factory=list, description="Input field names/labels")
    has_hidden_fields: bool = Field(default=False, description="Whether form has hidden inputs")
    hidden_field_names: list[str] = Field(
        default_factory=list, description="Names of hidden input fields"
    )


class TimerInfo(BaseModel):
    """Information about a countdown timer found on the page."""

    text: str = Field(default="", description="Timer display text, e.g. '02:30:00'")
    nearby_text: str = Field(default="", description="Text near the timer element")
    is_counting_down: bool = Field(default=False, description="Whether actively counting down")
    seconds_remaining: int | None = Field(
        default=None, description="Seconds remaining if parseable"
    )


class PageMeta(BaseModel):
    """Metadata about the scanned page."""

    title: str = Field(default="", description="Page title")
    description: str = Field(default="", description="Meta description")
    page_type: str = Field(
        default="unknown",
        description="Detected page type: checkout, signup, subscription, landing, unknown",
    )


class ScanRequest(BaseModel):
    """Request body for the POST /api/scan endpoint."""

    url: str = Field(default="", description="URL of the scanned page")
    page_text: str = Field(default="", description="Extracted visible text from the page")
    buttons: list[ButtonInfo] = Field(default_factory=list, description="Button elements found")
    links: list[LinkInfo] = Field(default_factory=list, description="Link elements found")
    checkboxes: list[CheckboxInfo] = Field(
        default_factory=list, description="Checkbox elements found"
    )
    forms: list[FormInfo] = Field(default_factory=list, description="Form elements found")
    timers: list[TimerInfo] = Field(
        default_factory=list, description="Countdown timers found"
    )
    meta: PageMeta = Field(default_factory=PageMeta, description="Page metadata")

    @model_validator(mode="before")
    @classmethod
    def populate_url(cls, data):
        if isinstance(data, dict):
            if not data.get("url"):
                meta = data.get("meta") or {}
                if isinstance(meta, dict) and meta.get("url"):
                    data["url"] = meta["url"]
                else:
                    data["url"] = "https://unknown-website.com"
        return data


class ScanResponse(BaseModel):
    """Response body returned from the POST /api/scan endpoint."""

    scan_id: str = Field(..., description="Unique identifier for this scan")
    url: str = Field(..., description="URL that was scanned")
    risk_score: int = Field(
        ..., ge=0, le=100, description="Overall risk score from 0 to 100"
    )
    risk_level: str = Field(
        ..., description="Risk level: Low, Medium, High, or Critical"
    )
    total_patterns: int = Field(..., description="Total number of dark patterns detected")
    patterns: list[DetectedPattern] = Field(
        default_factory=list, description="List of detected dark patterns"
    )
    recommendations: list[str] = Field(
        default_factory=list, description="High-level recommendations for the user"
    )
    scanned_at: datetime = Field(..., description="Timestamp when the scan was performed")
