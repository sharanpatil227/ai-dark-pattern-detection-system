"""
Sneaking detection rule.

Detects preselected checkboxes and options that add items, subscriptions,
or consent without explicit user action.
"""

import re
from app.models.pattern import DetectedPattern
from app.models.scan import ScanRequest

RULE_ID_PREFIX = "SN"

# Keywords near checkboxes that indicate sneaky additions
SNEAKY_CHECKBOX_KEYWORDS = [
    "subscribe", "newsletter", "marketing", "promotional",
    "add to cart", "add insurance", "protection plan", "warranty",
    "travel insurance", "travel protection", "trip protection",
    "priority", "express", "upgrade", "premium",
    "donation", "donate", "contribute", "charity",
    "opt in", "opt-in", "agree to receive", "send me",
    "yes, i want", "yes, sign me up",
    "share my data", "share my information",
    "third party", "third-party", "partners",
]

# Keywords for form hidden fields that indicate sneaking
SNEAKY_HIDDEN_FIELD_NAMES = [
    "addon", "add_on", "add-on",
    "insurance", "protection", "warranty",
    "subscribe", "newsletter", "marketing",
    "donation", "tip", "gratuity",
    "upgrade", "premium", "priority",
    "upsell", "cross_sell",
]


class SneakingRule:
    """Rule for detecting sneaking dark patterns."""

    category = "Sneaking"
    rule_id_prefix = RULE_ID_PREFIX

    def detect(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """Run sneaking detection on scan data."""
        patterns_found: list[DetectedPattern] = []

        # Check preselected checkboxes
        self._check_checkboxes(scan_data, patterns_found)

        # Check forms for sneaky hidden fields
        self._check_forms(scan_data, patterns_found)

        # Check page text for sneaky add-on language
        self._check_page_text(scan_data, patterns_found)

        return patterns_found

    def _check_checkboxes(
        self, scan_data: ScanRequest, patterns_found: list[DetectedPattern]
    ) -> None:
        """Check checkboxes that are pre-checked with sneaky labels."""
        for i, cb in enumerate(scan_data.checkboxes):
            if not cb.is_checked:
                continue  # Only care about pre-checked boxes

            combined_text = f"{cb.label} {cb.nearby_text}".lower()

            for keyword in SNEAKY_CHECKBOX_KEYWORDS:
                if keyword in combined_text:
                    # Determine severity based on what's being snuck in
                    severity = "High"
                    if keyword in ("insurance", "protection plan", "warranty",
                                   "travel insurance", "travel protection",
                                   "trip protection", "upgrade", "premium"):
                        severity = "Critical"
                    elif keyword in ("newsletter", "marketing", "promotional",
                                     "send me", "opt in", "opt-in"):
                        severity = "Medium"

                    patterns_found.append(
                        DetectedPattern(
                            category=self.category,
                            severity=severity,
                            confidence=0.90,
                            evidence=(
                                f"Pre-checked checkbox: '{cb.label}' "
                                f"(keyword: '{keyword}')"
                            ),
                            explanation=(
                                f"A checkbox related to '{keyword}' is pre-selected, "
                                "meaning the user would opt in without explicit action. "
                                "This is a sneaking pattern that adds items or consent by default."
                            ),
                            recommendation=(
                                "Uncheck this checkbox if you don't want this option. "
                                "It was pre-selected to catch inattentive users."
                            ),
                            detection_method="rule",
                            rule_id=f"{RULE_ID_PREFIX}-CB-{i}",
                        )
                    )
                    break  # One match per checkbox

    def _check_forms(
        self, scan_data: ScanRequest, patterns_found: list[DetectedPattern]
    ) -> None:
        """Check forms for hidden fields that may sneakily add items."""
        for i, form in enumerate(scan_data.forms):
            if not form.has_hidden_fields:
                continue

            for hidden_name in form.hidden_field_names:
                hidden_lower = hidden_name.lower()
                for keyword in SNEAKY_HIDDEN_FIELD_NAMES:
                    if keyword in hidden_lower:
                        patterns_found.append(
                            DetectedPattern(
                                category=self.category,
                                severity="High",
                                confidence=0.70,
                                evidence=(
                                    f"Hidden form field '{hidden_name}' "
                                    f"in form (action: '{form.action}')"
                                ),
                                explanation=(
                                    f"A hidden form field named '{hidden_name}' suggests "
                                    "an item or subscription may be added without the user's "
                                    "knowledge. Hidden fields for add-ons are a sneaking tactic."
                                ),
                                recommendation=(
                                    "Review what will be submitted with this form. "
                                    "Hidden fields may add charges or subscriptions."
                                ),
                                detection_method="rule",
                                rule_id=f"{RULE_ID_PREFIX}-FORM-{i}",
                            )
                        )
                        break

    def _check_page_text(
        self, scan_data: ScanRequest, patterns_found: list[DetectedPattern]
    ) -> None:
        """Check page text for sneaky addition language."""
        sneaky_text_patterns = [
            (
                r"(?:added|included)\s+(?:to\s+(?:your\s+)?(?:cart|order|basket))\s+(?:for\s+(?:your|added)\s+(?:protection|convenience|safety))",
                "Item automatically added to cart under the guise of protection or convenience",
            ),
            (
                r"(?:we'?ve?\s+)?(?:selected|chosen|picked|added)\s+(?:the\s+)?(?:recommended|best|optimal)\s+(?:plan|option|coverage|protection)\s+for\s+you",
                "An option was pre-selected on the user's behalf without explicit consent",
            ),
        ]

        for i, (pattern, explanation) in enumerate(sneaky_text_patterns):
            match = re.search(pattern, scan_data.page_text.lower())
            if match:
                patterns_found.append(
                    DetectedPattern(
                        category=self.category,
                        severity="High",
                        confidence=0.75,
                        evidence=f"Page text: '{match.group(0)}'",
                        explanation=explanation,
                        recommendation=(
                            "Review your cart or order carefully. "
                            "Items may have been added without your explicit consent."
                        ),
                        detection_method="rule",
                        rule_id=f"{RULE_ID_PREFIX}-TXT-{i}",
                    )
                )
