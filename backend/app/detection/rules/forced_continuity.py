"""
Forced Continuity detection rule.

Detects subscription traps where free trials automatically convert to
paid subscriptions, or where cancellation terms are buried in fine print.
"""

import re
from app.models.pattern import DetectedPattern
from app.models.scan import ScanRequest

RULE_ID_PREFIX = "FC"

# Composite patterns that combine free trial with automatic billing
FORCED_CONTINUITY_PATTERNS: list[tuple[str, str, str]] = [
    # "free trial" + "automatically" + "charged/billed/renewed"
    (
        r"free\s+(?:\d+[- ](?:day|week|month)\s+)?trial[\s\S]{0,160}?(?:automatically|auto[- ]?)\s*(?:charge[ds]?|bill(?:ed|ing)?|renew(?:ed|s|al)?|convert(?:ed|s)?|continue[ds]?|transition)",
        "Critical",
        "Free trial automatically converts to a paid subscription. "
        "Users may be charged without explicit re-consent.",
    ),
    # "trial ends" + "charged/billed"
    (
        r"(?:trial|promotional?\s+period)\s+(?:ends?|expir(?:es?|ation))[^.]{0,80}(?:charge[ds]?|bill(?:ed|ing)?|debit(?:ed)?)",
        "Critical",
        "After the trial period ends, the user will be automatically charged. "
        "This transition may not be clearly communicated.",
    ),
    # "cancel before" + "avoid being charged"
    (
        r"cancel\s+(?:before|prior\s+to|within)[^.]{0,60}(?:avoid|prevent)\s+(?:being\s+)?(?:charge[ds]?|bill(?:ed|ing)?)",
        "High",
        "Terms require cancellation before a deadline to avoid charges, "
        "indicating automatic billing will begin.",
    ),
    # "$X.XX/month after trial"
    (
        r"\$\d+(?:\.\d{2})?\s*/\s*(?:month|mo|week|wk|year|yr)\s+(?:after|following|when)\s+(?:trial|free\s+period)",
        "High",
        "Paid subscription pricing shown after free trial, "
        "indicating automatic conversion to paid plan.",
    ),
    # "You will be charged" + "after your free/trial"
    (
        r"(?:you\s+will|you'?ll)\s+be\s+(?:charge[ds]?|bill(?:ed|ing)?)[^.]{0,80}(?:after|following|when|once)\s+(?:your\s+)?(?:free|trial)",
        "Critical",
        "Explicit warning that the user will be charged after the trial period, "
        "indicating forced continuity.",
    ),
    # "Subscription will begin/start/activate"
    (
        r"(?:subscription|membership|plan)\s+will\s+(?:begin|start|activate|commence)[^.]{0,60}(?:after|following|when)\s+(?:trial|free\s+period)",
        "High",
        "Subscription automatically begins after the trial without explicit user action.",
    ),
    # "by signing up you agree" + "recurring" + "charge/payment"
    (
        r"(?:by\s+(?:signing\s+up|subscribing|starting|registering))[^.]{0,100}(?:recurring|automatic|auto)\s+(?:charge|payment|billing|debit)",
        "High",
        "Agreeing to sign up also consents to recurring automatic charges, "
        "which may be buried in terms.",
    ),
    # "No commitment" but also "billed monthly" (contradictory)
    (
        r"no\s+(?:commitment|obligation|contract)[^.]{0,100}(?:bill(?:ed|ing)?|charge[ds]?)\s+(?:monthly|weekly|annually|yearly)",
        "Medium",
        "Claims of 'no commitment' alongside regular billing language may be contradictory.",
    ),
]

# Keywords that reinforce forced continuity when combined
TRIAL_KEYWORDS = ["free trial", "trial period", "try free", "try for free", "free for"]
BILLING_KEYWORDS = [
    "automatically charged", "auto-renew", "auto renew", "recurring charge",
    "recurring payment", "billed automatically", "charged automatically",
    "subscription fee", "will be charged", "billing will begin",
    "payment will start", "renews automatically", "continuous subscription",
    "ongoing subscription",
]


class ForcedContinuityRule:
    """Rule for detecting forced continuity dark patterns."""

    category = "Forced Continuity"
    rule_id_prefix = RULE_ID_PREFIX

    def detect(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """Run forced continuity detection on scan data."""
        patterns_found: list[DetectedPattern] = []

        page_text_lower = scan_data.page_text.lower()

        # Check composite regex patterns
        for i, (pattern, severity, explanation) in enumerate(FORCED_CONTINUITY_PATTERNS):
            match = re.search(pattern, page_text_lower)
            if match:
                matched_text = match.group(0)
                # Trim evidence to reasonable length
                evidence_text = matched_text[:150]
                patterns_found.append(
                    DetectedPattern(
                        category=self.category,
                        severity=severity,
                        confidence=0.85,
                        evidence=f"Text found: '{evidence_text}'",
                        explanation=explanation,
                        recommendation=(
                            "Set a calendar reminder before the trial ends. "
                            "Note the exact cancellation procedure and deadline."
                        ),
                        detection_method="rule",
                        rule_id=f"{RULE_ID_PREFIX}-TXT-{i}",
                    )
                )

        # Keyword co-occurrence check: trial keyword + billing keyword in same page
        has_trial = any(kw in page_text_lower for kw in TRIAL_KEYWORDS)
        has_billing = any(kw in page_text_lower for kw in BILLING_KEYWORDS)

        if has_trial and has_billing and not patterns_found:
            # Only add if regex patterns didn't catch it (avoid duplicates)
            found_trial = next(kw for kw in TRIAL_KEYWORDS if kw in page_text_lower)
            found_billing = next(kw for kw in BILLING_KEYWORDS if kw in page_text_lower)
            patterns_found.append(
                DetectedPattern(
                    category=self.category,
                    severity="High",
                    confidence=0.70,
                    evidence=(
                        f"Found '{found_trial}' and '{found_billing}' on the same page"
                    ),
                    explanation=(
                        "The page mentions both a free trial and automatic billing, "
                        "suggesting the trial converts to a paid subscription automatically."
                    ),
                    recommendation=(
                        "Read the fine print carefully. This free trial likely "
                        "auto-converts to a paid subscription. Set a reminder to cancel if needed."
                    ),
                    detection_method="rule",
                    rule_id=f"{RULE_ID_PREFIX}-KW-COMBO",
                )
            )

        # Check buttons for trial signup that may hide billing info
        self._check_trial_buttons(scan_data, patterns_found)

        return patterns_found

    def _check_trial_buttons(
        self, scan_data: ScanRequest, patterns_found: list[DetectedPattern]
    ) -> None:
        """Check for trial signup buttons that hide billing terms."""
        trial_button_keywords = [
            "start free trial", "try free", "start trial",
            "begin free trial", "get free trial", "claim free trial",
            "try it free", "start my free",
        ]
        for i, btn in enumerate(scan_data.buttons):
            btn_lower = btn.text.lower().strip()
            for keyword in trial_button_keywords:
                if keyword in btn_lower:
                    # Check if nearby text mentions billing
                    nearby_lower = btn.nearby_text.lower()
                    billing_nearby = any(
                        bk in nearby_lower for bk in BILLING_KEYWORDS
                    )
                    if billing_nearby:
                        patterns_found.append(
                            DetectedPattern(
                                category=self.category,
                                severity="High",
                                confidence=0.75,
                                evidence=(
                                    f"Button '{btn.text}' with billing terms nearby: "
                                    f"'{btn.nearby_text[:80]}'"
                                ),
                                explanation=(
                                    "A 'free trial' button has billing/charging terms in "
                                    "nearby small text, suggesting automatic paid conversion."
                                ),
                                recommendation=(
                                    "Read all text near this button carefully before clicking. "
                                    "You may be committing to a paid subscription."
                                ),
                                detection_method="rule",
                                rule_id=f"{RULE_ID_PREFIX}-BTN-{i}",
                            )
                        )
                    break
