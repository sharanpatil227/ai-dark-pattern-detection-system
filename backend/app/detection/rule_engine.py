"""
Rule-based detection engine for dark patterns.
Executes all registered rules against scan data and aggregates detections.
"""

import logging
from app.models.pattern import DetectedPattern
from app.models.scan import ScanRequest
from app.detection.rules import ALL_RULES

logger = logging.getLogger(__name__)


class RuleEngine:
    """Executes rule-based dark pattern detection on scan data."""

    def __init__(self):
        self.rules = ALL_RULES

    def detect(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """
        Run all rule-based detectors on the provided scan data.
        Returns a list of all detected dark patterns.
        """
        all_patterns: list[DetectedPattern] = []

        for rule in self.rules:
            try:
                patterns = rule.detect(scan_data)
                if patterns:
                    all_patterns.extend(patterns)
            except Exception as e:
                logger.error("Error executing rule %s: %s", getattr(rule, "category", type(rule).__name__), e)

        return all_patterns

