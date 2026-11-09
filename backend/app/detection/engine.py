"""
Main Detection Engine orchestrating rule-based, NLP, and DOM analysis layers.
Aggregates, deduplicates, and computes comprehensive risk assessment.
"""

import uuid
import logging
from datetime import datetime

from app.models.scan import ScanRequest, ScanResponse
from app.models.pattern import DetectedPattern
from app.detection.rule_engine import RuleEngine
from app.detection.nlp_engine import NLPEngine
from app.detection.dom_analyzer import DOMAnalyzer
from app.utils.scoring import (
    calculate_risk_score,
    determine_risk_level,
    generate_recommendations,
)

logger = logging.getLogger(__name__)


class DetectionEngine:
    """Orchestrates all dark pattern detection subsystems."""

    def __init__(self):
        self.rule_engine = RuleEngine()
        self.nlp_engine = NLPEngine()
        self.dom_analyzer = DOMAnalyzer()

    def scan(self, scan_data: ScanRequest) -> ScanResponse:
        """Execute full multi-layer detection pipeline on the scan payload."""
        scan_id = str(uuid.uuid4())
        scanned_at = datetime.utcnow()

        raw_patterns: list[DetectedPattern] = []

        # 1. Rule-based detection
        try:
            rule_patterns = self.rule_engine.detect(scan_data)
            raw_patterns.extend(rule_patterns)
        except Exception as e:
            logger.error("Error during rule engine execution: %s", e)

        # 2. DOM and structural analysis
        try:
            dom_patterns = self.dom_analyzer.analyze(scan_data)
            raw_patterns.extend(dom_patterns)
        except Exception as e:
            logger.error("Error during DOM analyzer execution: %s", e)

        # 3. NLP text classification
        try:
            nlp_patterns = self.nlp_engine.detect(scan_data)
            raw_patterns.extend(nlp_patterns)
        except Exception as e:
            logger.error("Error during NLP engine execution: %s", e)

        # Deduplicate detections
        deduped_patterns = self._deduplicate_patterns(raw_patterns)

        # Calculate final scoring
        risk_score = calculate_risk_score(deduped_patterns)
        risk_level = determine_risk_level(risk_score)
        recommendations = generate_recommendations(deduped_patterns)

        return ScanResponse(
            scan_id=scan_id,
            url=scan_data.url,
            risk_score=risk_score,
            risk_level=risk_level,
            total_patterns=len(deduped_patterns),
            patterns=deduped_patterns,
            recommendations=recommendations,
            scanned_at=scanned_at,
        )

    def _deduplicate_patterns(self, patterns: list[DetectedPattern]) -> list[DetectedPattern]:
        """
        Deduplicate patterns with the same category and substantially similar evidence.
        Prefers rule-based detections if confidence is equal or higher.
        """
        unique_patterns: list[DetectedPattern] = []
        seen_keys: set[str] = set()

        for p in patterns:
            # Create a simplified key based on category and normalized evidence snippet
            evidence_snippet = p.evidence[:40].lower().strip()
            key = f"{p.category}:{evidence_snippet}"

            if key not in seen_keys:
                seen_keys.add(key)
                unique_patterns.append(p)
            else:
                # If seen, check if current is higher confidence
                for idx, existing in enumerate(unique_patterns):
                    existing_snippet = existing.evidence[:40].lower().strip()
                    if f"{existing.category}:{existing_snippet}" == key:
                        if p.confidence > existing.confidence:
                            unique_patterns[idx] = p
                        break

        return unique_patterns

