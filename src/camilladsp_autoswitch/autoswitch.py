"""
CamillaDSP Autoswitch daemon.

Responsibilities of this module:
- Read the runtime state (flags.py)
- Resolve which YAML configuration should be active
- Validate the YAML BEFORE applying it
- Apply the configuration only if it is safe
- Never break audio output
- Never crash the daemon
- Avoid log spam on repeated failures

This module DOES NOT:
- Decide DSP logic
- Parse or deeply inspect YAML contents
- Perform validation beyond safety checks
"""

from pathlib import Path
import logging
import time

from camilladsp_autoswitch.flags import load_state
from camilladsp_autoswitch.validator import validate

# -----------------------------------------------------------------------------
# Configuration paths
# -----------------------------------------------------------------------------

# Base directory where CamillaDSP profile YAML files are stored.
# This is intentionally fixed for now (system-wide configuration).
CONFIG_BASE_DIR = Path("/etc/camilladsp")

# Expected naming convention:
#   music.yml
#   cinema.yml
#   cinema_night.yml
#   music_lowlevel.yml
#
# Experimental YAML is always provided as an absolute path via runtime state.


# -----------------------------------------------------------------------------
# Logging configuration
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [autoswitch] %(levelname)s: %(message)s",
)

log = logging.getLogger("camilladsp-autoswitch")


# -----------------------------------------------------------------------------
# Internal daemon state (used to avoid log spam)
# -----------------------------------------------------------------------------

# Last YAML path evaluated by the daemon
_last_yaml: Path | None = None

# Last validation result:
#   True  -> valid
#   False -> invalid
#   None  -> never evaluated
_last_validation_ok: bool | None = None


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def resolve_yaml_path(state) -> Path:
    """
    Resolve which YAML file should be used based on the current runtime state.

    Priority order:
    1. Experimental YAML (absolute path)
    2. Profile + variant (relative to CONFIG_BASE_DIR)

    NOTE:
    This function does NOT validate the YAML file.
    """
    if state.experimental_yml:
        return Path(state.experimental_yml)

    name = state.profile

    if state.variant and state.variant != "normal":
        name = f"{name}_{state.variant}"

    return CONFIG_BASE_DIR / f"{name}.yml"


def apply_yaml(yaml_path: Path):
    """
    Apply a validated YAML configuration.

    IMPORTANT:
    This function is intentionally a stub and serves as a single
    integration point for future mechanisms such as:
    - camillapy
    - CamillaDSP HTTP API
    - FIFO or signal-based reload

    For now, it only logs the action.
    """
    log.info("Applying YAML: %s", yaml_path)
    # TODO: integrate actual CamillaDSP reload mechanism


# -----------------------------------------------------------------------------
# Core autoswitch logic
# -----------------------------------------------------------------------------

def autoswitch_once():
    """
    Execute a single autoswitch evaluation cycle.

    Safety guarantees:
    - Never raises uncaught exceptions
    - Never applies an invalid YAML
    - Logs only on meaningful state changes
    """
    global _last_yaml, _last_validation_ok

    state = load_state()
    yaml_path = resolve_yaml_path(state)

    yaml_changed = yaml_path != _last_yaml

    result = validate(yaml_path)

    # -------------------------
    # Invalid YAML
    # -------------------------
    if not result.valid:
        # Log only if:
        # - this is a new YAML path
        # - or the previous state was not already invalid
        if yaml_changed or _last_validation_ok is not False:
            log.error(
                "YAML validation failed, refusing to apply. Reason: %s",
                result.reason,
            )

        _last_yaml = yaml_path
        _last_validation_ok = False
        return

    # -------------------------
    # Valid YAML
    # -------------------------
    if yaml_changed or _last_validation_ok is not True:
        log.info("YAML validated successfully: %s", yaml_path)

    apply_yaml(yaml_path)

    _last_yaml = yaml_path
    _last_validation_ok = True


def run(interval: float = 2.0):
    """
    Main daemon loop.

    - Runs indefinitely
    - Evaluates state periodically
    - Absolute fail-safe: never crashes
    """
    log.info("CamillaDSP autoswitch daemon started")

    while True:
        try:
            autoswitch_once()
        except Exception as e:
            # Final fail-safe: the daemon must never die
            log.exception("Unexpected error in autoswitch loop: %s", e)

        time.sleep(interval)


# -----------------------------------------------------------------------------
# Manual execution / debugging
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    run()
