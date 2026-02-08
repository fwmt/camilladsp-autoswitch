"""
Tests for the default media player policy.

This policy decides which profile should be active
based solely on media player activity.
"""

from camilladsp_autoswitch.policy import (
    media_player_policy,
    PolicyDecision,
)


def test_policy_media_active_returns_cinema():
    """
    When media is active (e.g. Kodi running),
    the policy must select the cinema profile.
    """
    decision = media_player_policy(media_active=True)

    assert isinstance(decision, PolicyDecision)
    assert decision.profile == "cinema"
    assert decision.variant is None
    assert decision.reason == "media_active"


def test_policy_media_inactive_returns_music():
    """
    When media is inactive,
    the policy must fall back to the music profile.
    """
    decision = media_player_policy(media_active=False)

    assert isinstance(decision, PolicyDecision)
    assert decision.profile == "music"
    assert decision.variant is None
    assert decision.reason == "media_inactive"
