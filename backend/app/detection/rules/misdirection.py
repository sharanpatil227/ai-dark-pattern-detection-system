"""
Misdirection detection rule.

Detects visual misdirection where accept/agree buttons are significantly
more prominent than reject/decline buttons, or where the UI steers
users toward a specific choice through visual design.
"""

import re
from app.models.pattern import DetectedPattern
from app.models.scan import ScanRequest

RULE_ID_PREFIX = "MD"

# Accept/agree button keywords
ACCEPT_KEYWORDS = [
    "accept", "agree", "yes", "continue", "ok", "okay", "confirm",
    "subscribe", "sign up", "sign me up", "get started", "start",
    "buy now", "add to cart", "purchase", "checkout", "proceed",
    "i agree", "i accept", "got it", "allow", "enable",
    "upgrade", "go premium", "try premium", "yes, i want",
    "submit", "join", "join now", "activate",
]

# Reject/decline button keywords
REJECT_KEYWORDS = [
    "decline", "reject", "no", "cancel", "skip", "not now",
    "no thanks", "no thank you", "maybe later", "dismiss",
    "close", "not interested", "i disagree", "deny",
    "opt out", "opt-out", "keep current", "keep basic",
    "no, thanks", "i'll pass", "not right now", "remind me later",
]

# CSS class patterns indicating visual prominence
PROMINENT_CLASSES = [
    "primary", "cta", "highlight", "featured", "accent",
    "btn-primary", "btn-success", "btn-danger", "btn-warning",
    "bg-blue", "bg-green", "bg-red", "bg-orange",
    "large", "lg", "xl", "big", "bold", "emphasized",
    "main-action", "main-cta", "hero-button",
]

SUBTLE_CLASSES = [
    "secondary", "tertiary", "ghost", "outline", "link",
    "btn-link", "btn-outline", "btn-text", "btn-ghost",
    "text-only", "plain", "subtle", "muted", "dimmed",
    "small", "sm", "xs", "tiny", "mini",
    "dismiss", "skip-btn",
]


def _parse_pixel_size(size_str: str) -> float | None:
    """Parse a CSS size string to pixels (approximate)."""
    if not size_str:
        return None
    try:
        nums = re.findall(r"[\d.]+", size_str)
        if not nums:
            return None
        val = float(nums[0])
        if "em" in size_str.lower():
            return val * 16  # approximate
        if "rem" in size_str.lower():
            return val * 16
        return val  # assume px
    except (ValueError, IndexError):
        return None


class MisdirectionRule:
    """Rule for detecting misdirection dark patterns via visual design."""

    category = "Misdirection"
    rule_id_prefix = RULE_ID_PREFIX

    def detect(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """Run misdirection detection on scan data."""
        patterns_found: list[DetectedPattern] = []

        # Find accept and reject buttons
        accept_buttons = []
        reject_buttons = []

        for btn in scan_data.buttons:
            btn_lower = btn.text.lower().strip()
            if any(kw in btn_lower for kw in ACCEPT_KEYWORDS):
                accept_buttons.append(btn)
            elif any(kw in btn_lower for kw in REJECT_KEYWORDS):
                reject_buttons.append(btn)

        # Compare accept vs reject button prominence
        if accept_buttons and reject_buttons:
            self._compare_button_prominence(
                accept_buttons, reject_buttons, patterns_found
            )

        # Check for visually hidden reject options in links
        self._check_hidden_reject_links(scan_data, patterns_found)

        # Check for visual steering through class names
        self._check_class_based_steering(
            accept_buttons, reject_buttons, patterns_found
        )

        return patterns_found

    def _compare_button_prominence(
        self,
        accept_buttons: list,
        reject_buttons: list,
        patterns_found: list[DetectedPattern],
    ) -> None:
        """Compare the visual prominence of accept vs reject buttons."""
        for accept_btn in accept_buttons:
            for reject_btn in reject_buttons:
                issues: list[str] = []

                # Size comparison
                if accept_btn.width > 0 and reject_btn.width > 0:
                    if accept_btn.width > reject_btn.width * 1.5:
                        issues.append(
                            f"accept button is {accept_btn.width / reject_btn.width:.1f}x wider"
                        )
                if accept_btn.height > 0 and reject_btn.height > 0:
                    if accept_btn.height > reject_btn.height * 1.3:
                        issues.append(
                            f"accept button is {accept_btn.height / reject_btn.height:.1f}x taller"
                        )

                # Font size comparison
                accept_font = _parse_pixel_size(accept_btn.font_size)
                reject_font = _parse_pixel_size(reject_btn.font_size)
                if accept_font and reject_font and accept_font > reject_font * 1.3:
                    issues.append(
                        f"accept font ({accept_btn.font_size}) is larger than "
                        f"reject font ({reject_btn.font_size})"
                    )

                # Color comparison: accept has bg color, reject doesn't (or is muted)
                accept_has_color = bool(
                    accept_btn.background_color
                    and accept_btn.background_color.lower()
                    not in ("", "transparent", "none", "inherit", "rgba(0, 0, 0, 0)")
                )
                reject_has_color = bool(
                    reject_btn.background_color
                    and reject_btn.background_color.lower()
                    not in ("", "transparent", "none", "inherit", "rgba(0, 0, 0, 0)")
                )
                if accept_has_color and not reject_has_color:
                    issues.append(
                        "accept button has a prominent background color while reject is transparent/plain"
                    )

                if issues:
                    severity = "High" if len(issues) >= 2 else "Medium"
                    patterns_found.append(
                        DetectedPattern(
                            category=self.category,
                            severity=severity,
                            confidence=0.80,
                            evidence=(
                                f"Accept: '{accept_btn.text}' vs Reject: '{reject_btn.text}' — "
                                + "; ".join(issues)
                            ),
                            explanation=(
                                "The accept/agree button is visually much more prominent than "
                                "the decline/reject button. This visual asymmetry steers users "
                                "toward accepting by making the alternative less noticeable."
                            ),
                            recommendation=(
                                "Read all options carefully. The less prominent option "
                                "(decline/reject) may be the one you actually want."
                            ),
                            detection_method="dom",
                            rule_id=f"{RULE_ID_PREFIX}-BTN-ASYM",
                        )
                    )
                    return  # One detection is sufficient

    def _check_hidden_reject_links(
        self, scan_data: ScanRequest, patterns_found: list[DetectedPattern]
    ) -> None:
        """Check if reject/decline options are hidden as small links instead of buttons."""
        for i, link in enumerate(scan_data.links):
            link_lower = link.text.lower().strip()
            is_reject = any(kw in link_lower for kw in REJECT_KEYWORDS)
            if not is_reject:
                continue

            issues: list[str] = []

            # Check for small font
            font_px = _parse_pixel_size(link.font_size)
            if font_px is not None and font_px < 11:
                issues.append(f"very small font ({link.font_size})")

            # Check for muted color
            if link.color:
                muted_indicators = [
                    "#999", "#aaa", "#bbb", "#ccc", "#888", "#777",
                    "gray", "grey", "silver", "rgba(0,0,0,0.4",
                    "rgba(0, 0, 0, 0.4", "rgba(0,0,0,0.3",
                ]
                if any(m in link.color.lower() for m in muted_indicators):
                    issues.append(f"muted color ({link.color})")

            if not link.is_visible:
                issues.append("link is hidden")

            if issues:
                patterns_found.append(
                    DetectedPattern(
                        category=self.category,
                        severity="Medium",
                        confidence=0.75,
                        evidence=(
                            f"Reject link '{link.text}' with issues: {', '.join(issues)}"
                        ),
                        explanation=(
                            "The reject/decline option is presented as a small, "
                            "hard-to-see link rather than a clear button, "
                            "making it easy to miss."
                        ),
                        recommendation=(
                            "Look for small or gray text links near the main action button. "
                            "The opt-out option is intentionally made less visible."
                        ),
                        detection_method="dom",
                        rule_id=f"{RULE_ID_PREFIX}-LNK-{i}",
                    )
                )

    def _check_class_based_steering(
        self,
        accept_buttons: list,
        reject_buttons: list,
        patterns_found: list[DetectedPattern],
    ) -> None:
        """Check CSS classes for visual prominence steering."""
        for accept_btn in accept_buttons:
            accept_classes_lower = accept_btn.classes.lower()
            accept_prominent = any(
                cls in accept_classes_lower for cls in PROMINENT_CLASSES
            )
            if not accept_prominent:
                continue

            for reject_btn in reject_buttons:
                reject_classes_lower = reject_btn.classes.lower()
                reject_subtle = any(
                    cls in reject_classes_lower for cls in SUBTLE_CLASSES
                )

                if reject_subtle:
                    # Already flagged by prominence comparison? Check for duplicates
                    already_found = any(
                        p.rule_id and p.rule_id.startswith(f"{RULE_ID_PREFIX}-BTN")
                        for p in patterns_found
                    )
                    if not already_found:
                        patterns_found.append(
                            DetectedPattern(
                                category=self.category,
                                severity="Medium",
                                confidence=0.70,
                                evidence=(
                                    f"Accept button '{accept_btn.text}' uses prominent CSS classes "
                                    f"({accept_btn.classes}), while reject button '{reject_btn.text}' "
                                    f"uses subtle classes ({reject_btn.classes})"
                                ),
                                explanation=(
                                    "CSS styling is used to visually emphasize the accept option "
                                    "and de-emphasize the reject option, steering users toward accepting."
                                ),
                                recommendation=(
                                    "Both options should be equally visible. "
                                    "Consider the less prominent option carefully."
                                ),
                                detection_method="dom",
                                rule_id=f"{RULE_ID_PREFIX}-CLS",
                            )
                        )
                        return
