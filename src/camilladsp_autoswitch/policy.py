"""
Policy definitions for CamillaDSP Autoswitch.

A policy is a pure decision function:
- it receives facts (e.g. media activity)
- it returns a decision
- it has NO side effects

This file defines the default media player policy.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PolicyDecision:
    """
    Result of a policy evaluation.

    Attributes:
        profile: Logical profile name (e.g. 'music', 'cinema')
        variant: Optional profile variant (e.g. 'night', 'lowlevel')
        reason: Human-readable reason for the decision
    """
    profile: str
    variant: Optional[str]
    reason: str


def media_player_policy(media_active: bool) -> PolicyDecision:
    """
    Default autoswitch policy.

    Rule:
        - If media player is active → cinema
        - Otherwise → music

    Args:
        media_active: True if a media player (e.g. Kodi) is running

    Returns:
        PolicyDecision describing which profile should be active
    """
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
