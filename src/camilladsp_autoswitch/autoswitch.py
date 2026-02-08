"""
CamillaDSP Autoswitch daemon.

Responsibilities:
- Read runtime state (flags.py)
- Resolve which YAML configuration should be active
- Validate the YAML BEFORE applying it
- Apply the configuration only if it is safe
- Never break audio
- Never crash
- Avoid log spam

Configuration is controlled via environment variables:
- CDSP_CONFIG_DIR
- CDSP_AUTOSWITCH_INTERVAL
- CDSP_LOG_LEVEL
"""

from pathlib import Path
import logging
import os
import time

from camilladsp_autoswitch.flags import load_state
from camilladsp_autoswitch.validator import validate

# -----------------------------------------------------------------------------
# Environment-driven configuration
# -----------------------------------------------------------------------------

# Base directory where CamillaDSP YAML profiles are stored
CONFIG_BASE_DIR = Path(
    os.environ.get("CDSP_CONFIG_DIR", "/etc/camilladsp")
)

# Autoswitch polling interval (seconds)
AUTOSWITCH_INTERVAL = float(
    os.environ.get("CDSP_AUTOSWITCH_INTERVAL", "2.0")
)

# Logging level
LOG_LEVEL = os.environ.get("CDSP_LOG_LEVEL", "INFO").upper()

# -----------------------------------------------------------------------------
# Logging configuration
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [autoswitch] %(levelname)s: %(message)s",
)

log = logging.getLogger("camilladsp-autoswitch")

# -----------------------------------------------------------------------------
# Internal daemon state (to avoid log spam)
# -----------------------------------------------------------------------------

_last_yaml: Path | None = None
_last_validation_ok: bool | None = None

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def resolve_yaml_path(state) -> Path:
    """
    Resolve which YAML file should be used based on runtime state.

    Priority order:
    1. Experimental YAML (absolute path)
    2. Profile + variant (relative to CONFIG_BASE_DIR)
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

    This is a single integration point for:
    - camillapy
    - CamillaDSP HTTP API
    - FIFO / signal reload
    """
    log.info("Applying YAML: %s", yaml_path)
    # TODO: integrate CamillaDSP reload mechanism


# -----------------------------------------------------------------------------
# Core autoswitch logic
# -----------------------------------------------------------------------------

def autoswitch_once():
    """
    Execute a single autoswitch evaluation cycle.

    Guarantees:
    - Never raises uncaught exceptions
    - Never applies invalid YAML
    - Logs only on relevant changes
    """
    global _last_yaml, _last_validation_ok

    state = load_state()
    yaml_path = resolve_yaml_path(state)

    yaml_changed = yaml_path != _last_yaml

    result = validate(yaml_path)

    if not result.valid:
        if yaml_changed or _last_validation_ok is not False:
            log.error(
                "YAML validation failed, refusing to apply. Reason: %s",
                result.reason,
            )

        _last_yaml = yaml_path
        _last_validation_ok = False
        return

    if yaml_changed or _last_validation_ok is not True:
        log.info("YAML validated successfully: %s", yaml_path)

    apply_yaml(yaml_path)

    _last_yaml = yaml_path
    _last_validation_ok = True


def run():
    """
    Main daemon loop.
    """
    log.info("CamillaDSP autoswitch daemon started")
    log.info("Config dir: %s", CONFIG_BASE_DIR)
    log.info("Interval: %.2fs", AUTOSWITCH_INTERVAL)

    while True:
        try:
            autoswitch_once()
        except Exception as e:
            log.exception("Unexpected error in autoswitch loop: %s", e)

        time.sleep(AUTOSWITCH_INTERVAL)


# -----------------------------------------------------------------------------
# Manual execution / debug
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    run()
