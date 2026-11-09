"""
DOM and structural analyzer for detecting deceptive user interface patterns.
Analyzes layout, visual asymmetry, element prominence, and hidden options.
"""

import re
import logging
from app.models.pattern import DetectedPattern
from app.models.scan import ScanRequest

logger = logging.getLogger(__name__)


class DOMAnalyzer:
    """Analyzes DOM structure, visual hierarchy, and element attributes."""

    def analyze(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """Run structural and DOM analysis on the scan request."""
        patterns: list[DetectedPattern] = []

        patterns.extend(self._analyze_button_asymmetry(scan_data))
        patterns.extend(self._analyze_hidden_checkbox_manipulation(scan_data))
        patterns.extend(self._analyze_faint_links(scan_data))
        patterns.extend(self._analyze_form_manipulation(scan_data))

        return patterns

    def _analyze_button_asymmetry(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """Detect extreme visual discrepancy between positive and negative action buttons."""
        patterns: list[DetectedPattern] = []
        buttons = scan_data.buttons

        if len(buttons) < 2:
            return patterns

        accept_keywords = ["accept", "agree", "allow", "continue", "yes", "subscribe", "buy now", "sign up", "join"]
        reject_keywords = ["reject", "decline", "manage", "cancel", "no", "settings", "options", "skip", "opt out"]

        accept_btns = []
        reject_btns = []

        for btn in buttons:
            txt = btn.text.lower().strip()
            if any(k in txt for k in accept_keywords) and not any(k in txt for k in reject_keywords):
                accept_btns.append(btn)
            elif any(k in txt for k in reject_keywords):
                reject_btns.append(btn)

        for a_btn in accept_btns:
            for r_btn in reject_btns:
                # Compare dimensions if provided
                if a_btn.width > 0 and r_btn.width > 0:
                    area_accept = a_btn.width * a_btn.height
                    area_reject = r_btn.width * r_btn.height

                    # If accept button is more than 3x larger than reject option
                    if area_accept > 0 and area_reject > 0 and (area_accept / area_reject) >= 3.0:
                        patterns.append(
                            DetectedPattern(
                                category="Misdirection",
                                severity="High",
                                confidence=0.85,
                                evidence=f"Accept button '{a_btn.text}' ({a_btn.width}x{a_btn.height}px) is significantly larger than Decline option '{r_btn.text}' ({r_btn.width}x{r_btn.height}px)",
                                explanation="The interface visually prioritizes the desired action while suppressing the alternative through size disparity.",
                                recommendation="Examine the less prominent option carefully before clicking the dominant action button.",
                                detection_method="dom",
                                rule_id="DOM-ASYMM-SIZE",
                            )
                        )
                        return patterns

                # Check if reject button is marked hidden or invisible
                if not r_btn.is_visible and a_btn.is_visible:
                    patterns.append(
                        DetectedPattern(
                            category="Misdirection",
                            severity="Critical",
                            confidence=0.92,
                            evidence=f"Decline option '{r_btn.text}' is hidden or has zero visibility while Accept button '{a_btn.text}' is visible.",
                            explanation="The opt-out or reject mechanism is hidden from view, forcing users towards consent.",
                            recommendation="Look for hidden menus, expanders, or settings to access opt-out choices.",
                            detection_method="dom",
                            rule_id="DOM-HIDDEN-REJECT",
                        )
                    )
                    return patterns

        return patterns

    def _analyze_hidden_checkbox_manipulation(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """Detect checkboxes pre-selected with vague or missing labels."""
        patterns: list[DetectedPattern] = []
        for i, cb in enumerate(scan_data.checkboxes):
            if cb.is_checked:
                # Pre-checked with very faint or empty label
                if not cb.label.strip() or len(cb.label.strip()) < 3:
                    patterns.append(
                        DetectedPattern(
                            category="Sneaking",
                            severity="High",
                            confidence=0.88,
                            evidence=f"Pre-checked checkbox (name: '{cb.name}') without an explicit visible label.",
                            explanation="A pre-selected input lacks a clear label, which may surreptitiously opt the user into terms or recurring charges.",
                            recommendation="Uncheck any unexplained pre-selected boxes.",
                            detection_method="dom",
                            rule_id=f"DOM-SNEAK-NOLABEL-{i}",
                        )
                    )
        return patterns

    def _analyze_faint_links(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """Detect tiny or faint cancellation/opt-out links."""
        patterns: list[DetectedPattern] = []
        cancellation_keywords = ["cancel", "unsubscribe", "opt out", "opt-out", "delete account"]

        for i, link in enumerate(scan_data.links):
            txt = link.text.lower().strip()
            if any(k in txt for k in cancellation_keywords):
                # Check for tiny font sizes (e.g., <= 10px or 0.7rem)
                font_match = re.search(r"(\d+(\.\d+)?)px", link.font_size)
                if font_match:
                    size = float(font_match.group(1))
                    if size <= 11.0:
                        patterns.append(
                            DetectedPattern(
                                category="Obstruction",
                                severity="Medium",
                                confidence=0.80,
                                evidence=f"Cancellation link '{link.text}' is rendered in very small text ({link.font_size}).",
                                explanation="Critical account cancellation or opt-out options are visually minimized to discourage user engagement.",
                                recommendation="Inspect small footer or fine-print links carefully to find essential account options.",
                                detection_method="dom",
                                rule_id=f"DOM-TINY-LINK-{i}",
                            )
                        )
        return patterns

    def _analyze_form_manipulation(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """Analyze forms for deceptive hidden inputs related to recurring billing or insurance."""
        patterns: list[DetectedPattern] = []
        suspicious_hidden_names = ["auto_renew", "subscribe", "opt_in", "warranty", "protection_plan", "tip", "donation", "addon"]

        for i, form in enumerate(scan_data.forms):
            if form.has_hidden_fields:
                for h_name in form.hidden_field_names:
                    lower_h = h_name.lower()
                    if any(s in lower_h for s in suspicious_hidden_names):
                        patterns.append(
                            DetectedPattern(
                                category="Sneaking",
                                severity="High",
                                confidence=0.82,
                                evidence=f"Form contains hidden input '{h_name}' related to optional add-ons or recurring actions.",
                                explanation="Form quietly packages an add-on or subscription into the submission payload via hidden fields.",
                                recommendation="Review invoice items and transaction summaries thoroughly before confirming payment.",
                                detection_method="dom",
                                rule_id=f"DOM-FORM-HIDDEN-{i}",
                            )
                        )
        return patterns

