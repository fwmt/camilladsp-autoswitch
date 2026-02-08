"""
Tests for autoswitch profile decision policy.
"""

from camilladsp_autoswitch.autoswitch import decide_profile
from camilladsp_autoswitch.flags import CDSPState


def test_manual_mode_preserves_profile():
    state = CDSPState(mode="manual", profile="music")

    result = decide_profile(state=state, media_active=True)

    assert result == "music"


def test_media_active_selects_cinema():
    state = CDSPState(mode="auto", profile="music")

    result = decide_profile(state=state, media_active=True)

    assert result == "cinema"


def test_no_media_selects_music():
    state = CDSPState(mode="auto", profile="cinema")

    result = decide_profile(state=state, media_active=False)

    assert result == "music"
