"""
Fake Urgency detection rule.

Detects artificial urgency tactics like countdown timers on non-event pages,
"only X left" claims, and "limited time" pressure phrases.
"""

import re
from app.models.pattern import DetectedPattern
from app.models.scan import ScanRequest

RULE_ID_PREFIX = "FU"

# Regex patterns for urgency text
URGENCY_TEXT_PATTERNS: list[tuple[str, str, str]] = [
    # "Only X left in stock / only X minutes left"
    (
        r"only\s+\d+\s+(?:left|remaining|available|minutes?|seconds?|hours?)\s*(?:in\s+stock|before)?",
        "High",
        "Claims of limited stock quantities or ticking deadlines create artificial scarcity pressure",
    ),
    # "Hurry! / Act now! / Don't miss out!"
    (
        r"\b(?:hurry|act\s+now|don'?t\s+miss\s+(?:out|this)?|rush|quick|last\s+chance|final\s+chance)\b[!.]?",
        "Medium",
        "Urgency language pressures users into hasty decisions",
    ),
    # "Offer expires in..." / "Deal ends in..."
    (
        r"(?:offer|deal|sale|discount|price)\s+(?:expires?|ends?|expiring|ending)\s+(?:in|soon|today|tonight|midnight)",
        "High",
        "Time-limited offer language creates pressure to act immediately",
    ),
    # "Limited time offer/deal"
    (
        r"\blimited\s+(?:time|period|availability)\s+(?:offer|deal|sale|discount|price|opportunity)",
        "Medium",
        "Generic 'limited time' claim may be permanently displayed to create false urgency",
    ),
    # "X people are viewing this right now"
    (
        r"\d+\s+(?:people|users?|visitors?|shoppers?|others?)\s+(?:are\s+)?(?:viewing|looking\s+at|watching|browsing)(?:\s+this)?(?:\s+right\s+now)?",
        "High",
        "Social proof urgency: showing viewer count pressures users into competing",
    ),
    # "X people bought this in the last hour"
    (
        r"\d+\s+(?:people|users?|customers?|buyers?)\s+(?:bought|purchased|ordered|signed\s+up)\s+(?:this\s+)?(?:in\s+the\s+last|today|recently)",
        "Medium",
        "Social proof urgency creates fear of missing out",
    ),
    # "Selling fast" / "Going fast"
    (
        r"\b(?:selling|going|moving|running\s+out)\s+fast\b",
        "Medium",
        "Vague claims of rapid sales create artificial pressure",
    ),
    # "This deal won't last"
    (
        r"(?:this|the)\s+(?:deal|offer|price|discount)\s+(?:won'?t|will\s+not|cannot|can'?t)\s+last",
        "Medium",
        "Unverifiable claim that the deal is about to disappear",
    ),
    # "Today only" / "Tonight only"
    (
        r"\b(?:today|tonight|this\s+hour)\s+only\b",
        "Medium",
        "Time-restricted language that may be displayed permanently",
    ),
    # "Before it's too late" / "Before they're gone"
    (
        r"before\s+(?:it'?s?\s+too\s+late|they'?re?\s+(?:gone|all\s+gone|sold\s+out))",
        "Medium",
        "Fear-inducing language about missing out",
    ),
]


class FakeUrgencyRule:
    """Rule for detecting fake urgency dark patterns."""

    category = "Fake Urgency"
    rule_id_prefix = RULE_ID_PREFIX

    def detect(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """Run fake urgency detection on scan data."""
        patterns_found: list[DetectedPattern] = []

        # Check page text for urgency phrases
        page_text_lower = scan_data.page_text.lower()
        for i, (pattern, severity, explanation) in enumerate(URGENCY_TEXT_PATTERNS):
            match = re.search(pattern, page_text_lower)
            if match:
                matched_text = match.group(0)
                patterns_found.append(
                    DetectedPattern(
                        category=self.category,
                        severity=severity,
                        confidence=0.80,
                        evidence=f"Text found: '{matched_text}'",
                        explanation=explanation,
                        recommendation=(
                            "Verify this urgency claim independently. "
                            "Artificial scarcity and countdown timers are common manipulation tactics."
                        ),
                        detection_method="rule",
                        rule_id=f"{RULE_ID_PREFIX}-TXT-{i}",
                    )
                )

        # Check button text for urgency
        urgency_button_words = [
            "hurry", "act now", "buy now before", "last chance",
            "don't miss", "limited", "expires",
        ]
        for i, btn in enumerate(scan_data.buttons):
            btn_lower = btn.text.lower()
            for word in urgency_button_words:
                if word in btn_lower:
                    patterns_found.append(
                        DetectedPattern(
                            category=self.category,
                            severity="Medium",
                            confidence=0.70,
                            evidence=f"Button text: '{btn.text}'",
                            explanation=(
                                f"Button uses urgency language ('{word}') to pressure immediate action"
                            ),
                            recommendation=(
                                "Don't let urgent button text rush your decision. "
                                "Take your time to evaluate the offer."
                            ),
                            detection_method="rule",
                            rule_id=f"{RULE_ID_PREFIX}-BTN-{i}",
                        )
                    )
                    break  # One match per button

        # Check timers
        self._check_timers(scan_data, patterns_found)

        return patterns_found

    def _check_timers(
        self, scan_data: ScanRequest, patterns_found: list[DetectedPattern]
    ) -> None:
        """Analyze countdown timers for suspicious urgency patterns."""
        # Suspicious timer indicators:
        # - Very short countdowns (< 10 min) on non-event pages
        # - Timer near purchase/checkout/subscribe text
        # - Multiple timers on a single page
        suspicious_nearby_keywords = [
            "buy", "purchase", "order", "checkout", "subscribe",
            "sign up", "add to cart", "deal", "offer", "sale",
            "discount", "price", "save", "free",
        ]

        is_event_page = scan_data.meta.page_type in ("event", "booking", "reservation")

        for i, timer in enumerate(scan_data.timers):
            if not timer.is_counting_down:
                continue

            is_suspicious = False
            explanation = ""

            # Check countdown timer on non-event page
            if not is_event_page:
                is_suspicious = True
                explanation = (
                    f"Active countdown timer '{timer.text}' on a non-event page "
                    "suggests artificial urgency designed to rush user checkout"
                )
            elif (
                timer.seconds_remaining is not None
                and timer.seconds_remaining < 600
            ):
                is_suspicious = True
                explanation = (
                    f"Very short countdown ({timer.seconds_remaining}s remaining) "
                    "suggests artificial urgency"
                )

            # Timer near purchase-related text
            if not is_suspicious:
                nearby_lower = timer.nearby_text.lower()
                matched_kw = [kw for kw in suspicious_nearby_keywords if kw in nearby_lower]
                if matched_kw:
                    is_suspicious = True
                    explanation = (
                        f"Countdown timer found near purchase-related text "
                        f"({', '.join(matched_kw[:3])}), likely creating artificial pressure"
                    )

            if is_suspicious:
                patterns_found.append(
                    DetectedPattern(
                        category=self.category,
                        severity="High",
                        confidence=0.75,
                        evidence=f"Timer: '{timer.text}', near: '{timer.nearby_text[:80]}'",
                        explanation=explanation,
                        recommendation=(
                            "This countdown timer may be artificial. "
                            "Try refreshing the page or visiting later to see if it resets."
                        ),
                        detection_method="rule",
                        rule_id=f"{RULE_ID_PREFIX}-TMR-{i}",
                    )
                )

        # Multiple timers on one page is suspicious
        active_timers = [t for t in scan_data.timers if t.is_counting_down]
        if len(active_timers) >= 2:
            patterns_found.append(
                DetectedPattern(
                    category=self.category,
                    severity="High",
                    confidence=0.80,
                    evidence=f"Found {len(active_timers)} active countdown timers on one page",
                    explanation="Multiple countdown timers on a single page is a strong indicator of artificial urgency",
                    recommendation=(
                        "Multiple timers on one page are a red flag. "
                        "This is a high-pressure tactic—take your time."
                    ),
                    detection_method="rule",
                    rule_id=f"{RULE_ID_PREFIX}-MULTI-TMR",
                )
            )
