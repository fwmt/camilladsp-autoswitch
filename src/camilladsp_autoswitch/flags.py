"""
Runtime state management for camilladsp-autoswitch.

This module is the SINGLE SOURCE OF TRUTH for the autoswitch runtime state.

Design goals:
- Extremely robust (never break audio)
- Safe for concurrent access (atomic writes)
- Clear separation between DEV and PROD
- Minimal dependencies
"""

from dataclasses import dataclass, asdict
from pathlib import Path
import json
import os
from typing import Optional


# ============================================================================
# Runtime state location
# ============================================================================
#
# Production (systemd):
#   /run/cdsp/state.json
#
# Development / testing:
#   Override with environment variable:
#     export CDSP_STATE_DIR=/tmp/cdsp-test
#
# Rationale:
# - /run is tmpfs, cleared on reboot (perfect for runtime state)
# - systemd services can safely write here as root
# - developers should NEVER write to /run directly
#

STATE_DIR = Path(
    os.environ.get("CDSP_STATE_DIR", "/run/cdsp")
)

STATE_FILE = STATE_DIR / "state.json"


# ============================================================================
# Runtime State Model
# ============================================================================

@dataclass
class CDSPState:
    """
    Central runtime state for camilladsp-autoswitch.

    This structure defines ALL externally visible runtime decisions.

    Fields:
    - mode:
        "auto"   → autoswitch decides profile automatically
        "manual" → user forces profile via CLI

    - profile:
        Base profile name (e.g. music, cinema)

    - variant:
        Variant of the base profile
        (normal, night, lowlevel, etc.)

    - experimental_yml:
        Absolute path to an experimental YAML file.
        When set, it overrides profile + variant resolution.

    - status:
        Human-readable status field.
        Reserved for future diagnostics (OK / ERROR / DEGRADED).
    """

    mode: str = "auto"
    profile: str = "music"
    variant: str = "normal"
    experimental_yml: Optional[str] = None
    status: str = "OK"


# ============================================================================
# Load state (FAIL-SAFE)
# ============================================================================

def load_state() -> CDSPState:
    """
    Load runtime state from disk.

    IMPORTANT BEHAVIOR:
    - If the state file does not exist → return defaults
    - If the file is corrupted / unreadable → return defaults
    - This function must NEVER raise an exception

    Rationale:
    Audio must NEVER stop because of a broken state file.
    """

    if not STATE_FILE.exists():
        return CDSPState()

    try:
        data = json.loads(STATE_FILE.read_text())
        return CDSPState(**data)
    except Exception:
        # Absolute fail-safe:
        # Never propagate errors caused by corrupted state.
        return CDSPState()


# ============================================================================
# Save state (ATOMIC + EXPLICIT ERRORS)
# ============================================================================

def save_state(state: CDSPState):
    """
    Atomically persist runtime state to disk.

    Guarantees:
    - Directory is created if missing
    - Writes are atomic (no partial files)
    - Permission errors are explicit and user-friendly

    This function IS ALLOWED to raise PermissionError,
    because inability to save state is a real operational problem.
    """

    # Ensure state directory exists
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise PermissionError(
            f"Cannot write state to {STATE_DIR}. "
            f"Set CDSP_STATE_DIR for development or run as root."
        ) from e

    # Write to temporary file first
    tmp_file = STATE_FILE.with_suffix(".tmp")
    tmp_file.write_text(
        json.dumps(asdict(state), indent=2)
    )

    # Atomic replace (POSIX-safe on same filesystem)
    os.replace(tmp_file, STATE_FILE)


# ============================================================================
# Update state (STRICT + SAFE)
# ============================================================================

def update_state(**kwargs) -> CDSPState:
    """
    Update selected fields of the runtime state.

    Rules:
    - Only existing fields can be updated
    - Unknown fields are rejected (ValueError)
    - Changes are persisted atomically
    - Returns the updated state

    This function is the ONLY supported way to mutate runtime state.
    """

    state = load_state()

    for key, value in kwargs.items():
        if not hasattr(state, key):
            raise ValueError(f"Unknown state field: {key}")
        setattr(state, key, value)

    save_state(state)
    return state
