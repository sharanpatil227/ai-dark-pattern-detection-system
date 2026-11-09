"""
Scoring utilities for computing risk scores from detected patterns.
"""

from app.models.pattern import DetectedPattern

# Severity weight mapping
SEVERITY_WEIGHTS: dict[str, int] = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
}

# Risk level thresholds
RISK_LEVELS = [
    (0, 25, "Low"),
    (26, 50, "Medium"),
    (51, 75, "High"),
    (76, 100, "Critical"),
]


def calculate_risk_score(patterns: list[DetectedPattern]) -> int:
    """
    Calculate an overall risk score (0-100) from detected patterns.

    Factors:
    - Weighted sum of pattern severities.
    - Confidence levels of each detection.
    - Category diversity (more unique categories = higher risk).
    """
    if not patterns:
        return 0

    # Weighted severity sum, scaled by confidence
    weighted_sum = 0.0
    for p in patterns:
        weight = SEVERITY_WEIGHTS.get(p.severity, 1)
        weighted_sum += weight * p.confidence

    # Category diversity bonus: unique categories detected
    unique_categories = set(p.category for p in patterns)
    diversity_bonus = len(unique_categories) * 3  # +3 per unique category

    # Base score from weighted sum
    # Max expected weighted sum for normalization: ~20 (5 critical patterns at max confidence)
    max_expected_weighted = 20.0
    base_score = (weighted_sum / max_expected_weighted) * 70  # Up to 70 from severity

    # Total score
    raw_score = base_score + diversity_bonus

    # Clamp between 0 and 100
    return max(0, min(100, int(round(raw_score))))


def determine_risk_level(score: int) -> str:
    """Determine the risk level label from a numeric score."""
    for low, high, label in RISK_LEVELS:
        if low <= score <= high:
            return label
    return "Critical"  # fallback for score > 100


def generate_recommendations(patterns: list[DetectedPattern]) -> list[str]:
    """
    Generate high-level recommendations based on detected pattern categories.
    Returns deduplicated, actionable recommendations.
    """
    if not patterns:
        return ["No dark patterns detected. This page appears to use fair design practices."]

    recommendations: list[str] = []
    categories = set(p.category for p in patterns)

    if "Confirm Shaming" in categories:
        recommendations.append(
            "This site uses emotionally manipulative language to discourage opting out. "
            "Don't let guilt-tripping text influence your decisions."
        )
    if "Fake Urgency" in categories:
        recommendations.append(
            "Countdown timers and scarcity messages may be artificial. "
            "Verify urgency claims independently before rushing a purchase."
        )
    if "Sneaking" in categories:
        recommendations.append(
            "Check all checkboxes and pre-selected options carefully before submitting. "
            "Items or subscriptions may have been added without your explicit consent."
        )
    if "Hidden Costs" in categories:
        recommendations.append(
            "Review the final price carefully. Additional fees, charges, or taxes "
            "may appear late in the checkout process."
        )
    if "Forced Continuity" in categories:
        recommendations.append(
            "Free trial offers on this site may automatically convert to paid subscriptions. "
            "Set a reminder to cancel before the trial ends if you don't want to continue."
        )
    if "Obstruction" in categories:
        recommendations.append(
            "Cancelling or unsubscribing may be intentionally difficult. "
            "Look for account settings or contact support directly to cancel."
        )
    if "Misdirection" in categories:
        recommendations.append(
            "Visual design is being used to steer you toward a specific choice. "
            "Read all options carefully, including the less prominent ones."
        )

    # Add general recommendations if many patterns found
    if len(patterns) >= 5:
        recommendations.append(
            "This page uses multiple dark pattern techniques. Exercise extra caution "
            "and consider alternatives before proceeding."
        )

    severity_counts = {}
    for p in patterns:
        severity_counts[p.severity] = severity_counts.get(p.severity, 0) + 1
    if severity_counts.get("Critical", 0) >= 2:
        recommendations.append(
            "Multiple critical-severity dark patterns detected. "
            "Strongly consider leaving this site and finding an alternative."
        )

    return recommendations
