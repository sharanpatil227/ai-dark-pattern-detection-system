"""
Unit tests for rule-based dark pattern detection modules.
"""

from app.models.scan import ScanRequest, ButtonInfo, CheckboxInfo, TimerInfo
from app.detection.rules.confirm_shaming import ConfirmShamingRule
from app.detection.rules.fake_urgency import FakeUrgencyRule
from app.detection.rules.sneaking import SneakingRule
from app.detection.rules.hidden_costs import HiddenCostsRule
from app.detection.rules.forced_continuity import ForcedContinuityRule


def test_confirm_shaming_detection():
    rule = ConfirmShamingRule()
    scan = ScanRequest(
        url="https://test.com",
        buttons=[ButtonInfo(text="No thanks, I don't want to save money")],
    )
    results = rule.detect(scan)
    assert len(results) > 0
    assert results[0].category == "Confirm Shaming"
    assert "guilt" in results[0].explanation.lower() or "manipulative" in results[0].explanation.lower()


def test_fake_urgency_detection():
    rule = FakeUrgencyRule()
    scan = ScanRequest(
        url="https://test.com",
        page_text="Only 2 minutes left before deal expires! 3 people viewing right now!",
        timers=[TimerInfo(text="01:30", is_counting_down=True)],
    )
    results = rule.detect(scan)
    assert len(results) > 0
    assert any(r.category == "Fake Urgency" for r in results)


def test_sneaking_preselected_checkbox():
    rule = SneakingRule()
    scan = ScanRequest(
        url="https://test.com",
        checkboxes=[
            CheckboxInfo(label="Add extended warranty insurance for $19.99", is_checked=True),
        ],
    )
    results = rule.detect(scan)
    assert len(results) > 0
    assert any(r.category == "Sneaking" for r in results)


def test_hidden_costs_detection():
    rule = HiddenCostsRule()
    scan = ScanRequest(
        url="https://test.com",
        page_text="Total $50.00. Mandatory service charge of $15.00 added at checkout.",
    )
    results = rule.detect(scan)
    assert len(results) > 0
    assert any(r.category == "Hidden Costs" for r in results)


def test_forced_continuity_detection():
    rule = ForcedContinuityRule()
    scan = ScanRequest(
        url="https://test.com",
        page_text="Free 7-day trial. Automatically renews at $39.99 per month until cancelled.",
    )
    results = rule.detect(scan)
    assert len(results) > 0
    assert any(r.category == "Forced Continuity" for r in results)

