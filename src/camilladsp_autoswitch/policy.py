from dataclasses import dataclass
import os


@dataclass(frozen=True)
class PolicyDecision:
    profile: str
    variant: str | None
    reason: str


def media_player_policy(media_active: bool) -> PolicyDecision:
    if media_active:
        return PolicyDecision(
            profile="cinema",
            variant=None,
            reason="media_active",
        )
    return PolicyDecision(
        profile="music",
        variant=None,
        reason="media_inactive",
    )


def map_decision_to_profile(decision: PolicyDecision) -> PolicyDecision:
    """
    Apply environment-based profile remapping.

    IMPORTANT:
    - Must ALWAYS return a PolicyDecision
    - Must NEVER return a string
    """

    if decision.reason == "media_active":
        profile = os.getenv("CDSP_PROFILE_MEDIA_ACTIVE", decision.profile)
    elif decision.reason == "media_inactive":
        profile = os.getenv("CDSP_PROFILE_MEDIA_INACTIVE", decision.profile)
    else:
        # manual_mode or any future policy
        profile = decision.profile

    return PolicyDecision(
        profile=profile,
        variant=decision.variant,
        reason=decision.reason,
    )
