import os
import json
from pathlib import Path
import importlib

import pytest


def reload_runtime_state(tmp_path):
    """
    Reload the runtime_state module with a temporary state dir.
    """
    os.environ["CDSP_STATE_DIR"] = str(tmp_path)
    from camilladsp_autoswitch import runtime_state
    importlib.reload(runtime_state)
    return runtime_state


def test_default_state_when_missing(tmp_path):
    runtime_state = reload_runtime_state(tmp_path)
    state = runtime_state.load_state()

    assert state.mode == "auto"
    assert state.profile == "music"
    assert state.variant == "normal"
    assert state.experimental_yml is None
    assert state.status == "OK"


def test_state_persistence(tmp_path):
    runtime_state = reload_runtime_state(tmp_path)

    runtime_state.update_state(mode="manual", profile="cinema")
    state = runtime_state.load_state()

    assert state.mode == "manual"
    assert state.profile == "cinema"

    state_file = Path(tmp_path) / "state.json"
    assert state_file.exists()

    raw = json.loads(state_file.read_text())
    assert raw["mode"] == "manual"
    assert raw["profile"] == "cinema"


def test_partial_update_preserves_other_fields(tmp_path):
    runtime_state = reload_runtime_state(tmp_path)

    runtime_state.update_state(profile="cinema")
    runtime_state.update_state(variant="night")

    state = runtime_state.load_state()
    assert state.profile == "cinema"
    assert state.variant == "night"
    assert state.mode == "auto"  # unchanged


def test_invalid_field_rejected(tmp_path):
    runtime_state = reload_runtime_state(tmp_path)

    with pytest.raises(ValueError):
        runtime_state.update_state(nonexistent="boom")
