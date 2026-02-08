from dataclasses import dataclass, asdict
from pathlib import Path
import json
import os
from typing import Optional

# Runtime state location
# Default: /run/cdsp (systemd / production)
# Override via CDSP_STATE_DIR for development/testing
STATE_DIR = Path(
    os.environ.get("CDSP_STATE_DIR", "/run/cdsp")
)
STATE_FILE = STATE_DIR / "state.json"


@dataclass
class CDSPState:
    """
    Central runtime state for camilladsp-autoswitch.

    This file is the single source of truth for:
    - automatic vs manual mode
    - selected profile / variant
    - experimental YAML override
    """
    mode: str = "auto"              # auto | manual
    profile: str = "music"          # music | cinema
    variant: str = "normal"         # normal | night | lowlevel
    experimental_yml: Optional[str] = None
    status: str = "OK"


def load_state() -> CDSPState:
    """
    Load runtime state from /run.
    If missing or invalid, return defaults.
    """
    if not STATE_FILE.exists():
        return CDSPState()

    try:
        data = json.loads(STATE_FILE.read_text())
        return CDSPState(**data)
    except Exception:
        # Fail-safe: never break audio because of state corruption
        return CDSPState()


def save_state(state: CDSPState):
    """
    Atomically persist runtime state.
    """
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(asdict(state), indent=2))

    # Atomic replace
    os.replace(tmp, STATE_FILE)


def update_state(**kwargs) -> CDSPState:
    """
    Update selected fields of the runtime state.
    Unknown keys are rejected.
    """
    state = load_state()

    for key, value in kwargs.items():
        if not hasattr(state, key):
            raise ValueError(f"Unknown state field: {key}")
        setattr(state, key, value)

    save_state(state)
    return state
