"""
Hidden Costs detection rule.

Detects price-related patterns where additional fees, charges, shipping costs,
service fees, or taxes appear late or in small/hidden text.
"""

import re
from app.models.pattern import DetectedPattern
from app.models.scan import ScanRequest

RULE_ID_PREFIX = "HC"

# Hidden cost keyword patterns
HIDDEN_COST_PATTERNS: list[tuple[str, str, str]] = [
    # Service fee / handling fee / processing fee
    (
        r"(?:service|handling|processing|booking|convenience|platform|admin(?:istration)?)\s+fee\s*(?:[:]\s*)?\$?\d+",
        "High",
        "An additional fee is being charged that may not have been disclosed upfront",
    ),
    # Shipping not free / shipping charges
    (
        r"shipping\s+(?:&\s+handling\s+)?(?:fee|charge|cost)\s*(?:[:]\s*)?\$?\d+",
        "Medium",
        "Shipping charges appear separately and may not have been shown earlier",
    ),
    # Tax added at checkout
    (
        r"(?:estimated\s+)?(?:tax|taxes|vat|gst|sales\s+tax)\s*(?:[:]\s*)?\$?\d+",
        "Low",
        "Taxes are shown, which is standard practice but should be disclosed upfront",
    ),
    # "Price does not include"
    (
        r"price\s+(?:does\s+not|doesn'?t)\s+include",
        "High",
        "The displayed price omits certain costs, which will be added later",
    ),
    # Additional charges / extra charges
    (
        r"(?:additional|extra|surcharge|supplementary|mandatory)\s+(?:charge|fee|cost|payment)s?",
        "High",
        "Additional charges beyond the displayed price are present",
    ),
    # "Starting at / from" with small text showing real price
    (
        r"(?:starting|from)\s+(?:at\s+)?\$?\d+[./]\d+\s*(?:\*|†|‡)",
        "Medium",
        "Advertised price uses 'starting at' with an asterisk, suggesting the real price is higher",
    ),
    # Resort fee / destination fee / facility fee
    (
        r"(?:resort|destination|facility|amenity|cleaning|checkout)\s+fee",
        "High",
        "A mandatory fee is listed separately from the displayed price",
    ),
    # Gratuity/tip automatically added
    (
        r"(?:gratuity|tip|service\s+charge)\s+(?:of\s+)?\d+%?\s+(?:has\s+been\s+|is\s+|will\s+be\s+)?(?:automatically\s+)?(?:added|included|applied)",
        "High",
        "A tip or gratuity is being automatically added to the total",
    ),
    # "Prices shown are per person" (when not obvious)
    (
        r"prices?\s+(?:shown\s+)?(?:is|are)\s+per\s+(?:person|night|month|unit)",
        "Medium",
        "The price shown is per unit/person, which may not have been clear initially",
    ),
    # Cancellation fee / early termination fee
    (
        r"(?:cancellation|early\s+termination|restocking|return)\s+fee\s*(?:[:]\s*)?(?:\$?\d+|of\s+\d+%)",
        "High",
        "A cancellation or return fee exists that may deter the user from exercising their rights",
    ),
]


class HiddenCostsRule:
    """Rule for detecting hidden costs dark patterns."""

    category = "Hidden Costs"
    rule_id_prefix = RULE_ID_PREFIX

    def detect(self, scan_data: ScanRequest) -> list[DetectedPattern]:
        """Run hidden costs detection on scan data."""
        patterns_found: list[DetectedPattern] = []

        page_text_lower = scan_data.page_text.lower()

        # Check page text against hidden cost patterns
        for i, (pattern, severity, explanation) in enumerate(HIDDEN_COST_PATTERNS):
            match = re.search(pattern, page_text_lower)
            if match:
                patterns_found.append(
                    DetectedPattern(
                        category=self.category,
                        severity=severity,
                        confidence=0.80,
                        evidence=f"Text found: '{match.group(0)}'",
                        explanation=explanation,
                        recommendation=(
                            "Review the full price breakdown carefully. "
                            "Additional fees may significantly increase the total cost."
                        ),
                        detection_method="rule",
                        rule_id=f"{RULE_ID_PREFIX}-TXT-{i}",
                    )
                )

        # Check for drip pricing indicators: price appearing in multiple places
        # with different values
        self._check_price_discrepancies(scan_data, patterns_found)

        return patterns_found

    def _check_price_discrepancies(
        self, scan_data: ScanRequest, patterns_found: list[DetectedPattern]
    ) -> None:
        """
        Check for multiple different prices on the same page,
        which may indicate drip pricing (showing a low price first,
        then revealing the real cost later).
        """
        # Extract all dollar amounts from page text
        price_matches = re.findall(
            r"\$(\d+(?:\.\d{1,2})?)", scan_data.page_text
        )
        if len(price_matches) < 2:
            return

        prices = []
        for p in price_matches:
            try:
                prices.append(float(p))
            except ValueError:
                continue

        if len(prices) < 2:
            return

        # Filter out very small prices (likely shipping/tax amounts already shown)
        # and very large prices (totals), focus on mid-range
        sorted_prices = sorted(set(prices))

        # Check if there's a significant gap between a small displayed price
        # and a larger total (drip pricing signal)
        if len(sorted_prices) >= 2:
            smallest = sorted_prices[0]
            largest = sorted_prices[-1]

            # Only flag if the ratio is significant and smallest isn't trivially small
            if smallest > 1.0 and largest > smallest * 1.5:
                difference = largest - smallest
                # Only flag if the difference is meaningful
                if difference >= 5.0:
                    patterns_found.append(
                        DetectedPattern(
                            category=self.category,
                            severity="Medium",
                            confidence=0.55,
                            evidence=(
                                f"Multiple prices found: ${smallest:.2f} to ${largest:.2f} "
                                f"(difference: ${difference:.2f})"
                            ),
                            explanation=(
                                "Multiple price points on this page suggest potential drip pricing, "
                                "where the initially shown price is lower than the final cost."
                            ),
                            recommendation=(
                                "Compare the initially displayed price with the final total. "
                                "Look for fees added during checkout."
                            ),
                            detection_method="rule",
                            rule_id=f"{RULE_ID_PREFIX}-DRIP",
                        )
                    )
