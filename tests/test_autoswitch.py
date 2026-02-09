"""
Tests for autoswitch core decision logic.

These tests deliberately avoid:
- filesystem watchers
- CamillaDSP websocket
- time-based polling

Focus:
- YAML resolution
- Validation handling
- Safe behavior on errors
"""

from pathlib import Path
from unittest.mock import patch

from camilladsp_autoswitch.autoswitch import (
    resolve_yaml_path,
    autoswitch_once,
    _reset_internal_state,
)

from camilladsp_autoswitch.flags import CDSPState
from camilladsp_autoswitch.intent import SwitchIntent


@patch("camilladsp_autoswitch.autoswitch.apply_yaml")
@patch("camilladsp_autoswitch.autoswitch.validate")
@patch("camilladsp_autoswitch.autoswitch.build_intent_from_policy")
@patch("camilladsp_autoswitch.autoswitch.load_state")
def test_autoswitch_uses_intent_layer(
    mock_load_state,
    mock_build_intent,
    mock_validate,
    mock_apply,
):
    """
    autoswitch must build and execute an Intent,
    not act directly on PolicyDecision.
    """

    mock_load_state.return_value = CDSPState(
        mode="auto",
        profile="music",
        variant="normal",
    )

    mock_build_intent.return_value = SwitchIntent(
        profile="cinema",
        variant=None,
        reason="media_active",
    )

    mock_validate.return_value.valid = True
    mock_validate.return_value.reason = None

    autoswitch_once()

    mock_build_intent.assert_called_once()


def test_resolve_yaml_music_normal(tmp_path):
    state = CDSPState(profile="music", variant="normal")
    base = tmp_path

    path = resolve_yaml_path(state)

    # Default path is relative; filename is what matters
    assert path.name == "music.yml"


def test_resolve_yaml_cinema_night(tmp_path):
    state = CDSPState(profile="cinema", variant="night")

    path = resolve_yaml_path(state)
    assert path.name == "cinema_night.yml"


def test_resolve_yaml_experimental_overrides():
    state = CDSPState(
        profile="music",
        variant="normal",
        experimental_yml="/tmp/exp.yml",
    )

    path = resolve_yaml_path(state)
    assert path == Path("/tmp/exp.yml")


@patch("camilladsp_autoswitch.autoswitch.validate")
@patch("camilladsp_autoswitch.autoswitch.apply_yaml")
@patch("camilladsp_autoswitch.autoswitch.load_state")
def test_autoswitch_does_not_apply_invalid_yaml(
    mock_load_state,
    mock_apply,
    mock_validate,
):
    mock_load_state.return_value = CDSPState(profile="music")
    mock_validate.return_value.valid = False
    mock_validate.return_value.reason = "invalid yaml"

    autoswitch_once()

    mock_apply.assert_not_called()


@patch("camilladsp_autoswitch.autoswitch.validate")
@patch("camilladsp_autoswitch.autoswitch.apply_yaml")
@patch("camilladsp_autoswitch.autoswitch.load_state")
def test_autoswitch_applies_valid_yaml_once(
    mock_load_state,
    mock_apply,
    mock_validate,
):

    # 🔑 Reset internal autoswitch state for deterministic testing
    _reset_internal_state()

    mock_load_state.return_value = CDSPState(profile="music")
    mock_validate.return_value.valid = True
    mock_validate.return_value.reason = None

    autoswitch_once()
    autoswitch_once()  # second run, should not reapply

    mock_apply.assert_called_once()
