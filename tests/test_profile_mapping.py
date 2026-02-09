"""
Tests for mapping logical policy decisions to user-configured profiles.
"""

from camilladsp_autoswitch.policy import PolicyDecision
from camilladsp_autoswitch.autoswitch import map_decision_to_profile


def test_media_active_maps_to_default_profile(monkeypatch):
    """
    By default, media_active must map to 'cinema'.
    """
    monkeypatch.delenv("CDSP_PROFILE_MEDIA_ACTIVE", raising=False)

    decision = PolicyDecision(
        profile="cinema",
        variant=None,
        reason="media_active",
    )

    mapped = map_decision_to_profile(decision)

    assert mapped.profile == "cinema"
    assert mapped.reason == "media_active"


def test_media_inactive_maps_to_default_profile(monkeypatch):
    """
    By default, media_inactive must map to 'music'.
    """
    monkeypatch.delenv("CDSP_PROFILE_MEDIA_INACTIVE", raising=False)

    decision = PolicyDecision(
        profile="music",
        variant=None,
        reason="media_inactive",
    )

    mapped = map_decision_to_profile(decision)

    assert mapped.profile == "music"
    assert mapped.reason == "media_inactive"


def test_media_active_maps_to_custom_profile(monkeypatch):
    """
    Custom profile names must be honored via environment variables.
    """
    monkeypatch.setenv("CDSP_PROFILE_MEDIA_ACTIVE", "multichannel")

    decision = PolicyDecision(
        profile="cinema",
        variant=None,
        reason="media_active",
    )

    mapped = map_decision_to_profile(decision)

    assert mapped.profile == "multichannel"


def test_media_inactive_maps_to_custom_profile(monkeypatch):
    """
    Custom inactive profile must be honored via environment variables.
    """
    monkeypatch.setenv("CDSP_PROFILE_MEDIA_INACTIVE", "stereo")

    decision = PolicyDecision(
        profile="music",
        variant=None,
        reason="media_inactive",
    )

    mapped = map_decision_to_profile(decision)

    assert mapped.profile == "stereo"


def test_manual_mode_decision_is_not_modified():
    """
    Decisions not coming from media policy must pass through untouched.
    """
    decision = PolicyDecision(
        profile="custom",
        variant="night",
        reason="manual_mode",
    )

    mapped = map_decision_to_profile(decision)

    assert mapped.profile == "custom"
    assert mapped.variant == "night"
    assert mapped.reason == "manual_mode"
