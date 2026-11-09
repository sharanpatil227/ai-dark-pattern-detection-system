from app.detection.rules.confirm_shaming import ConfirmShamingRule
from app.detection.rules.fake_urgency import FakeUrgencyRule
from app.detection.rules.sneaking import SneakingRule
from app.detection.rules.hidden_costs import HiddenCostsRule
from app.detection.rules.forced_continuity import ForcedContinuityRule
from app.detection.rules.obstruction import ObstructionRule
from app.detection.rules.misdirection import MisdirectionRule

ALL_RULES = [
    ConfirmShamingRule(),
    FakeUrgencyRule(),
    SneakingRule(),
    HiddenCostsRule(),
    ForcedContinuityRule(),
    ObstructionRule(),
    MisdirectionRule(),
]

__all__ = [
    "ConfirmShamingRule",
    "FakeUrgencyRule",
    "SneakingRule",
    "HiddenCostsRule",
    "ForcedContinuityRule",
    "ObstructionRule",
    "MisdirectionRule",
    "ALL_RULES",
]
