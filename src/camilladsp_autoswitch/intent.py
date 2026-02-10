"""
Intent layer.

Responsible for expressing *what* the system intends to do,
not *how* it is executed.

This is the Use Case boundary.
"""

from dataclasses import dataclass
from camilladsp_autoswitch.events import PolicyDecision

@dataclass(frozen=True)
class SwitchIntent:
    """
    Intent to switch to a given profile/variant.
    """
    profile: str
    variant: str | None
    reason: str


def build_intent_from_policy(decision: PolicyDecision) -> SwitchIntent:
    """
    Translate a PolicyDecision into an executable intent.

    This function must:
    - be pure
    - have no side effects
    - contain no I/O
    """
    return SwitchIntent(
        profile=decision.profile,
        variant=decision.variant,
        reason=decision.reason,
    )
