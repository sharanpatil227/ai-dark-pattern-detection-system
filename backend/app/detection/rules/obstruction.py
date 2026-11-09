"""
Obstruction detection rule.

Detects patterns that make cancellation, unsubscription, or account deletion
intentionally difficult. E.g., hidden unsubscribe links, "call us to cancel",
multi-step cancellation flows.
"""

import re
from app.models.pattern import DetectedPattern
from app.models.scan import ScanRequest

RULE_ID_PREFIX = "OB"

# Patterns indicating obstructed cancellation
OBSTRUCTION_PATTERNS: list[tuple[str, str, str]] = [
    # "Call us to cancel" / "Phone us to cancel"
    (
        r"(?:call|phone|ring|contact)\s+(?:us|our\s+(?:team|support|customer\s+service))\s+(?:to|in\s+order\s+to)\s+(?:cancel|unsubscribe|end\s+(?:your\s+)?(?:subscription|membership|account))",
        "Critical",
        "Cancellation requires a phone call, which is a deliberate obstruction tactic "
        "designed to make cancelling difficult and enable save-attempts.",
    ),
    # "Visit our office/store to cancel"
    (
        r"(?:visit|come\s+to|go\s+to)\s+(?:our|a|the)\s+(?:office|store|branch|location)\s+(?:to|in\s+order\s+to)\s+(?:cancel|unsubscribe|close)",
        "Critical",
        "Requiring an in-person visit to cancel is a severe obstruction pattern.",
    ),
    # "Send a letter/mail to cancel"
    (
        r"(?:send|mail|post|write)\s+(?:a\s+)?(?:letter|written\s+(?:notice|request)|cancellation\s+(?:letter|request))\s+(?:to|at)",
        "Critical",
        "Requiring physical mail to cancel is a deliberate obstruction tactic.",
    ),
    # "Cancellation takes X business days"
    (
        r"cancel(?:lation)?\s+(?:takes?|requires?|may\s+take)\s+(?:up\s+to\s+)?\d+\s+(?:business\s+)?days",
        "High",
        "A long cancellation processing period delays users from actually ending service.",
    ),
    # "Cancel during business hours only"
    (
        r"cancel(?:lation)?\s+(?:is\s+)?(?:only\s+)?(?:available|possible|processed)\s+(?:during|between)\s+(?:business|office|working)\s+hours",
        "High",
        "Restricting cancellation to business hours makes it harder for users to cancel.",
    ),
    # "Complete X steps to cancel"
    (
        r"(?:complete|follow)\s+(?:these\s+)?(?:\d+|multiple|several)\s+steps?\s+to\s+cancel",
        "High",
        "Multi-step cancellation process is designed to tire users into giving up.",
    ),
    # "Are you sure" / multiple confirmations
    (
        r"(?:before\s+you\s+(?:cancel|go|leave)|are\s+you\s+sure\s+you\s+want\s+to\s+cancel)[^.]*(?:special\s+offer|discount|deal|reduced\s+price|stay\s+with\s+us|keep\s+your)",
        "High",
        "Cancellation flow includes save-attempt offers designed to obstruct the process.",
    ),
]

# Keywords in links that suggest hidden/hard-to-find cancel options
HIDDEN_CANCEL_KEYWORDS = [
    "unsubscribe", "cancel subscription", "cancel membership",
    "end subscription", "close account", "delete account",
    "opt out", "opt-out", "remove me", "stop emails",
]


class ObstructionRule:
    """Rule for detecting obstruction dark patterns."""

    category = "Obstruction"
    rule_id_prefix = RULE_ID_PREFIX

    def detect(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """Run obstruction detection on scan data."""
        patterns_found: list[DetectedPattern] = []

        page_text_lower = scan_data.page_text.lower()

        # Check text patterns
        for i, (pattern, severity, explanation) in enumerate(OBSTRUCTION_PATTERNS):
            match = re.search(pattern, page_text_lower)
            if match:
                patterns_found.append(
                    DetectedPattern(
                        category=self.category,
                        severity=severity,
                        confidence=0.85,
                        evidence=f"Text found: '{match.group(0)[:120]}'",
                        explanation=explanation,
                        recommendation=(
                            "You have the right to cancel easily. "
                            "In many jurisdictions, companies must provide online cancellation "
                            "if you signed up online. Check your consumer rights."
                        ),
                        detection_method="rule",
                        rule_id=f"{RULE_ID_PREFIX}-TXT-{i}",
                    )
                )

        # Check for hidden unsubscribe/cancel links
        self._check_hidden_cancel_links(scan_data, patterns_found)

        return patterns_found

    def _check_hidden_cancel_links(
        self, scan_data: ScanRequest, patterns_found: list[DetectedPattern]
    ) -> None:
        """Check for cancel/unsubscribe links that are hidden or hard to find."""
        for i, link in enumerate(scan_data.links):
            link_text_lower = link.text.lower()
            is_cancel_link = any(
                kw in link_text_lower for kw in HIDDEN_CANCEL_KEYWORDS
            )

            if not is_cancel_link:
                continue

            # Check if the link is hidden or has tiny font
            issues: list[str] = []

            if not link.is_visible:
                issues.append("link is hidden/invisible")

            # Check for very small font size
            if link.font_size:
                try:
                    size_val = float(re.findall(r"[\d.]+", link.font_size)[0])
                    unit = link.font_size.replace(str(size_val), "").strip().lower()
                    if unit == "px" and size_val < 10:
                        issues.append(f"very small font size ({link.font_size})")
                    elif unit == "em" and size_val < 0.7:
                        issues.append(f"very small font size ({link.font_size})")
                except (IndexError, ValueError):
                    pass

            # Check for low-contrast color (gray on white, etc.)
            if link.color:
                color_lower = link.color.lower().strip()
                low_contrast_colors = [
                    "#ccc", "#ddd", "#eee", "#999", "#aaa", "#bbb",
                    "lightgray", "lightgrey", "silver", "#c0c0c0",
                    "rgb(200", "rgb(204", "rgb(192", "rgb(170",
                    "rgba(0, 0, 0, 0.3", "rgba(0, 0, 0, 0.2",
                    "rgba(0,0,0,0.3", "rgba(0,0,0,0.2",
                ]
                if any(lc in color_lower for lc in low_contrast_colors):
                    issues.append(f"low-contrast color ({link.color})")

            if issues:
                patterns_found.append(
                    DetectedPattern(
                        category=self.category,
                        severity="High",
                        confidence=0.80,
                        evidence=(
                            f"Cancel/unsubscribe link '{link.text}' "
                            f"issues: {', '.join(issues)}"
                        ),
                        explanation=(
                            "The cancel or unsubscribe link is intentionally made hard to find "
                            f"({', '.join(issues)}). This is an obstruction pattern."
                        ),
                        recommendation=(
                            "Look carefully for the cancel/unsubscribe option. "
                            "It exists but has been made difficult to see or access."
                        ),
                        detection_method="rule",
                        rule_id=f"{RULE_ID_PREFIX}-LNK-{i}",
                    )
                )
