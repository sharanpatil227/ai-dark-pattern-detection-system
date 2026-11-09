"""
Pytest configuration and shared fixtures.
"""

import pytest
from app.models.scan import (
    ScanRequest,
    ButtonInfo,
    LinkInfo,
    CheckboxInfo,
    FormInfo,
    TimerInfo,
    PageMeta,
)


@pytest.fixture
def sample_clean_scan() -> ScanRequest:
    """Scan data with standard, non-deceptive interface elements."""
    return ScanRequest(
        url="https://fair-shop.example.com",
        page_text="Welcome to our store. We sell handmade wool sweaters. All taxes and shipping are calculated fairly at checkout.",
        buttons=[
            ButtonInfo(text="Add to Bag", width=120, height=40, is_visible=True),
            ButtonInfo(text="View Details", width=110, height=40, is_visible=True),
        ],
        links=[
            LinkInfo(text="Privacy Policy", href="/privacy", font_size="14px", is_visible=True),
            LinkInfo(text="Contact Support", href="/contact", font_size="14px", is_visible=True),
        ],
        checkboxes=[
            CheckboxInfo(label="I agree to terms", is_checked=False, is_visible=True),
        ],
        forms=[
            FormInfo(action="/checkout", method="post", fields=["name", "address"]),
        ],
        timers=[],
        meta=PageMeta(title="Fair Shop", description="A fair clothing store"),
    )


@pytest.fixture
def sample_dark_pattern_scan() -> ScanRequest:
    """Scan data with multiple prominent deceptive patterns."""
    return ScanRequest(
        url="https://deceptive-deal.example.com/checkout",
        page_text="Only 2 minutes left to finish your purchase! No thanks, I don't want to save money today. A mandatory processing fee of $12.99 applies. Free 7-day trial then $49.99/mo automatically charged.",
        buttons=[
            ButtonInfo(text="YES, CLAIM MY 70% DISCOUNT", width=300, height=60, is_visible=True),
            ButtonInfo(text="No, I prefer paying full price", width=80, height=20, is_visible=True),
        ],
        links=[
            LinkInfo(text="To cancel membership, call our hotline", href="/faq", font_size="9px", is_visible=True),
        ],
        checkboxes=[
            CheckboxInfo(label="Add $9.99 shipping insurance", is_checked=True, is_visible=True),
        ],
        forms=[
            FormInfo(
                action="/order",
                method="post",
                has_hidden_fields=True,
                hidden_field_names=["auto_renew", "warranty_plan"],
            )
        ],
        timers=[
            TimerInfo(text="00:01:45", is_counting_down=True, seconds_remaining=105),
        ],
        meta=PageMeta(title="Super Discount", description="Flash deal checkout"),
    )

