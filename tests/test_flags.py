import os
import json
from pathlib import Path
import importlib

import pytest


def reload_flags(tmp_path):
    """
    Reload the flags module with a temporary state dir.
    """
    os.environ["CDSP_STATE_DIR"] = str(tmp_path)
    from camilladsp_autoswitch import flags
    importlib.reload(flags)
    return flags


def test_default_state_when_missing(tmp_path):
    flags = reload_flags(tmp_path)
    state = flags.load_state()

    assert state.mode == "auto"
    assert state.profile == "music"
    assert state.variant == "normal"
    assert state.experimental_yml is None
    assert state.status == "OK"


def test_state_persistence(tmp_path):
    flags = reload_flags(tmp_path)

    flags.update_state(mode="manual", profile="cinema")
    state = flags.load_state()

    assert state.mode == "manual"
    assert state.profile == "cinema"

    state_file = Path(tmp_path) / "state.json"
    assert state_file.exists()

    raw = json.loads(state_file.read_text())
    assert raw["mode"] == "manual"
    assert raw["profile"] == "cinema"


def test_partial_update_preserves_other_fields(tmp_path):
    flags = reload_flags(tmp_path)

    flags.update_state(profile="cinema")
    flags.update_state(variant="night")

    state = flags.load_state()
    assert state.profile == "cinema"
    assert state.variant == "night"
    assert state.mode == "auto"  # unchanged


def test_invalid_field_rejected(tmp_path):
    flags = reload_flags(tmp_path)

    with pytest.raises(ValueError):
        flags.update_state(nonexistent="boom")
