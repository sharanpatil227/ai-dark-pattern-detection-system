"""
Confirm Shaming detection rule.

Detects emotionally manipulative opt-out text designed to guilt users
into not declining an offer. Examples:
- "No thanks, I don't want to save money"
- "No, I prefer paying full price"
- "I don't care about my health"
"""

import re
from app.models.pattern import DetectedPattern
from app.models.scan import ScanRequest

RULE_ID_PREFIX = "CS"

# Regex patterns for confirm-shaming phrases
SHAME_PATTERNS: list[tuple[str, str]] = [
    # "No, I don't want to <positive thing>"
    (
        r"\bno\b[,.]?\s*(?:thanks?|thank you)[,.]?\s*i\s+(?:don'?t|do\s+not)\s+(?:want|need|care)",
        "Opt-out text uses negative self-attribution to guilt the user",
    ),
    # "I prefer paying full price" / "I prefer to miss out"
    (
        r"\bi\s+prefer\s+(?:to\s+)?(?:pay(?:ing)?\s+full\s+price|miss(?:ing)?\s+out|not\s+sav(?:e|ing))",
        "Opt-out implies the user prefers a worse outcome",
    ),
    # "No, I hate saving" / "No, I hate discounts"
    (
        r"\bno\b[,.]?\s*i\s+(?:hate|dislike|don'?t\s+like)\s+(?:sav(?:e|ing)|discount|deal|bargain|money|health)",
        "Opt-out uses emotionally charged negative language",
    ),
    # "I don't care about <positive thing>"
    (
        r"\bi\s+(?:don'?t|do\s+not)\s+care\s+about\s+(?:my\s+)?(?:health|family|savings?|future|security|privacy|money|weight|body|diet|fitness)",
        "Opt-out text shames user about important life concerns",
    ),
    # "I'll pass on this amazing/incredible/exclusive offer"
    (
        r"\b(?:i'?ll?\s+pass|no\s+thanks?)\s+(?:on\s+)?(?:this\s+)?(?:amazing|incredible|exclusive|once.in.a.lifetime|great|fantastic|special|limited)",
        "Opt-out text emphasizes the supposed value being rejected",
    ),
    # "I'm not interested in <obvious good thing>"
    (
        r"\bi(?:'m|\s+am)\s+not\s+interested\s+in\s+(?:sav(?:e|ing)|discount|free|better|improv|protect|secur)",
        "Opt-out frames declining as rejecting something obviously good",
    ),
    # Manipulative dismiss buttons: "Maybe later, I don't want <benefit>"
    (
        r"maybe\s+later[,.]?\s+i\s+(?:don'?t|do\s+not)\s+(?:want|need)",
        "Dismiss option uses guilt-laden phrasing",
    ),
    # "Continue without <benefit>" where benefit is savings, protection, etc.
    (
        r"continue\s+without\s+(?:sav(?:e|ing)|protect(?:ion|ing)?|benefit|discount|security|insur(?:ance|ing))",
        "Decline option frames the user as giving up protection or savings",
    ),
]

# Simpler keyword-based patterns for button/link text
SHAME_KEYWORDS = [
    "no thanks, i don't want",
    "no, i don't want",
    "i prefer paying full price",
    "i don't need to save",
    "i hate saving",
    "i'll stay unprotected",
    "i don't care about",
    "no, i'll pass on",
    "i'm fine with paying more",
    "i don't want to save",
    "decline this offer",
    "reject discount",
    "continue without saving",
    "i'd rather not save",
    "no, i want to pay more",
    "no, i enjoy paying full price",
]


class ConfirmShamingRule:
    """Rule for detecting confirm-shaming dark patterns."""

    category = "Confirm Shaming"
    rule_id_prefix = RULE_ID_PREFIX

    def detect(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """Run confirm shaming detection on scan data."""
        patterns_found: list[DetectedPattern] = []

        # Check button text
        for i, btn in enumerate(scan_data.buttons):
            detections = self._check_text(
                btn.text, f"Button: '{btn.text}'", f"{RULE_ID_PREFIX}-BTN-{i}"
            )
            patterns_found.extend(detections)

        # Check link text
        for i, link in enumerate(scan_data.links):
            detections = self._check_text(
                link.text, f"Link: '{link.text}'", f"{RULE_ID_PREFIX}-LNK-{i}"
            )
            patterns_found.extend(detections)

        # Check page text for embedded confirm-shaming
        sentences = re.split(r"[.!?\n]+", scan_data.page_text)
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) < 5:
                continue
            detections = self._check_text(
                sentence, f"Page text: '{sentence[:120]}'", f"{RULE_ID_PREFIX}-TXT-{i}"
            )
            patterns_found.extend(detections)

        return patterns_found

    def _check_text(
        self, text: str, evidence_label: str, rule_id: str
    ) -> list[DetectedPattern]:
        """Check a text string against confirm-shaming patterns."""
        results: list[DetectedPattern] = []
        if not text or len(text.strip()) < 3:
            return results

        lower_text = text.lower().strip()

        # Check regex patterns
        for pattern, explanation in SHAME_PATTERNS:
            match = re.search(pattern, lower_text)
            if match:
                results.append(
                    DetectedPattern(
                        category=self.category,
                        severity="High",
                        confidence=0.85,
                        evidence=evidence_label,
                        explanation=explanation,
                        recommendation=(
                            "This text is designed to make you feel guilty about declining. "
                            "Make your decision based on your actual needs, not emotional pressure."
                        ),
                        detection_method="rule",
                        rule_id=rule_id,
                    )
                )
                return results  # One match per text element is enough

        # Check keyword patterns
        for keyword in SHAME_KEYWORDS:
            if keyword in lower_text:
                results.append(
                    DetectedPattern(
                        category=self.category,
                        severity="Medium",
                        confidence=0.75,
                        evidence=evidence_label,
                        explanation=(
                            f"Opt-out text contains confirm-shaming phrase: '{keyword}'"
                        ),
                        recommendation=(
                            "Don't let guilt-tripping language influence your decision. "
                            "This is a known manipulative design pattern."
                        ),
                        detection_method="rule",
                        rule_id=rule_id,
                    )
                )
                return results  # One match per text element is enough

        return results
