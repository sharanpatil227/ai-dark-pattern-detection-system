"""
Integration tests for the main detection engine and scoring system.
"""

from app.detection.engine import DetectionEngine
from app.utils.scoring import calculate_risk_score, determine_risk_level
from app.models.pattern import DetectedPattern


def test_detection_engine_clean_scan(sample_clean_scan):
    engine = DetectionEngine()
    result = engine.scan(sample_clean_scan)

    assert result.total_patterns == 0
    assert result.risk_score <= 15
    assert result.risk_level == "Low"


def test_detection_engine_dark_patterns(sample_dark_pattern_scan):
    engine = DetectionEngine()
    result = engine.scan(sample_dark_pattern_scan)

    assert result.total_patterns > 0
    assert result.risk_score >= 40
    assert result.risk_level in ["Medium", "High", "Critical"]
    assert len(result.recommendations) > 0


def test_scoring_weights():
    patterns = [
        DetectedPattern(
            category="Confirm Shaming",
            severity="High",
            confidence=0.9,
            evidence="No, I prefer paying full price",
            explanation="Guilt trip",
            recommendation="Ignore",
            detection_method="rule",
        ),
        DetectedPattern(
            category="Forced Continuity",
            severity="Critical",
            confidence=0.95,
            evidence="Free trial auto-renews at $99",
            explanation="Subscription trap",
            recommendation="Set reminder",
            detection_method="rule",
        ),
    ]

    score = calculate_risk_score(patterns)
    assert 20 <= score <= 100
    level = determine_risk_level(score)
    assert level in ["Medium", "High", "Critical"]

