"""
Natural Language Processing and Machine Learning classification engine.
Uses trained TF-IDF + LogisticRegression model to identify semantic dark patterns.
"""

import os
import re
import logging
from typing import Optional
import joblib

from app.config import settings
from app.models.pattern import DetectedPattern
from app.models.scan import ScanRequest

logger = logging.getLogger(__name__)


CATEGORY_SEVERITIES = {
    "Confirm Shaming": "High",
    "Fake Urgency": "High",
    "Forced Continuity": "Critical",
    "Hidden Costs": "High",
    "Sneaking": "High",
    "Obstruction": "Medium",
    "Misdirection": "High",
}

CATEGORY_RECOMMENDATIONS = {
    "Confirm Shaming": "Don't let guilt-tripping language pressure your choice. Decide based on your real preferences.",
    "Fake Urgency": "Verify if stock numbers or deadlines are genuine before making an impulsive decision.",
    "Forced Continuity": "Review billing terms. Check if a free trial automatically changes to an expensive recurring plan.",
    "Hidden Costs": "Inspect the final payment breakdown for surprise surcharges, platform fees, or mandatory add-ons.",
    "Sneaking": "Uncheck any pre-selected options or add-ons that you didn't deliberately choose.",
    "Obstruction": "Take note of account cancellation prerequisites before committing to subscriptions.",
    "Misdirection": "Look past visually highlighted primary buttons to locate neutral or decline options.",
}


class NLPEngine:
    """Classifies text segments using pre-trained ML model."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.ML_MODEL_PATH
        self.pipeline = None
        self._load_model()

    def _load_model(self) -> None:
        """Attempt to load the saved scikit-learn pipeline."""
        resolved_path = os.path.abspath(self.model_path)
        if not os.path.exists(resolved_path):
            # Also check relative to project root
            alt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), self.model_path)
            if os.path.exists(alt_path):
                resolved_path = alt_path
            else:
                logger.warning(
                    "ML model file not found at %s or %s. NLP engine will operate in fallback mode.",
                    resolved_path,
                    alt_path,
                )
                return

        try:
            self.pipeline = joblib.load(resolved_path)
            logger.info("Loaded ML model successfully from %s", resolved_path)
        except Exception as e:
            logger.error("Failed to load ML model from %s: %s", resolved_path, e)
            self.pipeline = None

    @property
    def is_loaded(self) -> bool:
        """Whether the model is loaded and ready."""
        return self.pipeline is not None

    def classify_text(self, text: str) -> tuple[str, float]:
        """
        Classify a single text snippet.
        Returns: (predicted_category, confidence)
        """
        if not self.is_loaded or not text or len(text.strip()) < 4:
            return ("Benign", 0.0)

        cleaned = text.strip()
        try:
            pred_cat = self.pipeline.predict([cleaned])[0]
            if hasattr(self.pipeline, "predict_proba"):
                probs = self.pipeline.predict_proba([cleaned])[0]
                classes = list(self.pipeline.classes_)
                idx = classes.index(pred_cat)
                confidence = float(probs[idx])
            else:
                confidence = 0.80

            return (pred_cat, confidence)
        except Exception as e:
            logger.error("Error during text classification: %s", e)
            return ("Benign", 0.0)

    def detect(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """
        Scan page text, button labels, link texts, and meta descriptions with the ML model.
        """
        patterns: list[DetectedPattern] = []
        if not self.is_loaded:
            return patterns

        # 1. Check button texts
        for btn in scan_data.buttons:
            if btn.text and len(btn.text.strip()) > 3:
                cat, conf = self.classify_text(btn.text)
                if cat != "Benign" and conf >= 0.60:
                    patterns.append(
                        DetectedPattern(
                            category=cat,
                            severity=CATEGORY_SEVERITIES.get(cat, "Medium"),
                            confidence=round(conf, 2),
                            evidence=f"Button text: '{btn.text}'",
                            explanation=f"Machine learning classifier identified semantic {cat.lower()} pattern.",
                            recommendation=CATEGORY_RECOMMENDATIONS.get(cat, "Proceed with caution."),
                            detection_method="nlp",
                            rule_id=None,
                        )
                    )

        # 2. Check link texts
        for link in scan_data.links:
            if link.text and len(link.text.strip()) > 4:
                cat, conf = self.classify_text(link.text)
                if cat != "Benign" and conf >= 0.65:
                    patterns.append(
                        DetectedPattern(
                            category=cat,
                            severity=CATEGORY_SEVERITIES.get(cat, "Medium"),
                            confidence=round(conf, 2),
                            evidence=f"Link text: '{link.text}'",
                            explanation=f"Semantic analysis detected deceptive {cat.lower()} phrasing in link.",
                            recommendation=CATEGORY_RECOMMENDATIONS.get(cat, "Review link carefully."),
                            detection_method="nlp",
                            rule_id=None,
                        )
                    )

        # 3. Check page text sentences (limit to top 100 sentences for performance)
        sentences = re.split(r"[.!?\n]+", scan_data.page_text)
        checked = 0
        for sentence in sentences:
            s = sentence.strip()
            if len(s) < 15 or len(s) > 200:
                continue
            if checked >= 60:
                break
            checked += 1

            cat, conf = self.classify_text(s)
            if cat != "Benign" and conf >= 0.70:
                patterns.append(
                    DetectedPattern(
                        category=cat,
                        severity=CATEGORY_SEVERITIES.get(cat, "Medium"),
                        confidence=round(conf, 2),
                        evidence=f"Page text: '{s}'",
                        explanation=f"Natural language model flagged text as exhibiting {cat.lower()} rhetoric.",
                        recommendation=CATEGORY_RECOMMENDATIONS.get(cat, "Carefully verify offer terms."),
                        detection_method="nlp",
                        rule_id=None,
                    )
                )

        return patterns

