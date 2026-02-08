"""
CamillaDSP Autoswitch daemon.

Responsibilities:
- Read runtime state (flags.py)
- Resolve which YAML configuration should be active
- Validate the YAML BEFORE applying it
- Apply the configuration using the official pycamilladsp client
- Never break audio
- Never crash the daemon
- Avoid log spam

Environment variables:
- CDSP_CONFIG_DIR
- CDSP_AUTOSWITCH_INTERVAL
- CDSP_LOG_LEVEL
- CDSP_CAMILLA_HOST
- CDSP_CAMILLA_PORT
"""

from pathlib import Path
import logging
import os
import time

from camilladsp_autoswitch.flags import load_state
from camilladsp_autoswitch.validator import validate

# Optional dependency: pycamilladsp
# The daemon MUST keep running even if this is not installed.
try:
    from camilladsp import CamillaDSP
except ImportError:
    CamillaDSP = None


# -----------------------------------------------------------------------------
# Environment-driven configuration
# -----------------------------------------------------------------------------

CONFIG_BASE_DIR = Path(
    os.environ.get("CDSP_CONFIG_DIR", "/etc/camilladsp")
)

AUTOSWITCH_INTERVAL = float(
    os.environ.get("CDSP_AUTOSWITCH_INTERVAL", "2.0")
)

LOG_LEVEL = os.environ.get("CDSP_LOG_LEVEL", "INFO").upper()

CAMILLA_HOST = os.environ.get("CDSP_CAMILLA_HOST", "127.0.0.1")
CAMILLA_PORT = int(os.environ.get("CDSP_CAMILLA_PORT", "1234"))


# -----------------------------------------------------------------------------
# Logging configuration
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [autoswitch] %(levelname)s: %(message)s",
)

log = logging.getLogger("camilladsp-autoswitch")


# -----------------------------------------------------------------------------
# Internal daemon state (used to avoid log spam and redundant reloads)
# -----------------------------------------------------------------------------

_last_yaml: Path | None = None
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
    """
    if state.experimental_yml:
        return Path(state.experimental_yml)

    name = state.profile

    if state.variant and state.variant != "normal":
        name = f"{name}_{state.variant}"

    return CONFIG_BASE_DIR / f"{name}.yml"


def apply_yaml(yaml_path: Path):
    """
    Apply a validated YAML configuration using the official pycamilladsp client.

    Safety rules:
    - pycamilladsp is optional
    - CamillaDSP may be offline
    - Any failure must be logged and NEVER crash the daemon
    """
    if CamillaDSP is None:
        log.warning(
            "pycamilladsp not installed, cannot apply configuration. "
            "Validation succeeded but reload is skipped."
        )
        return

    try:
        client = CamillaDSP(
            host=CAMILLA_HOST,
            port=CAMILLA_PORT,
        )

        # Set the configuration file path
        client.set_config_name(str(yaml_path))

        # Reload CamillaDSP to apply the new config
        client.reload()

        log.info("Configuration applied via CamillaDSP API: %s", yaml_path)

    except Exception as e:
        # Absolute fail-safe: never crash because of DSP connectivity
        log.error("Failed to apply configuration via CamillaDSP API: %s", e)


# -----------------------------------------------------------------------------
# Core autoswitch logic
# -----------------------------------------------------------------------------

def autoswitch_once():
    """
    Execute a single autoswitch evaluation cycle.

    Guarantees:
    - Never raises uncaught exceptions
    - Never applies invalid YAML
    - Avoids log spam on repeated failures
    - Avoids unnecessary reloads
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

    # Only apply if the YAML actually changed
    if yaml_changed:
        apply_yaml(yaml_path)

    _last_yaml = yaml_path
    _last_validation_ok = True


def run():
    """
    Main daemon loop.

    - Runs indefinitely
    - Polling-based (event-driven comes later)
    - Absolute fail-safe
    """
    log.info("CamillaDSP autoswitch daemon started")
    log.info("Config dir: %s", CONFIG_BASE_DIR)
    log.info("CamillaDSP endpoint: %s:%d", CAMILLA_HOST, CAMILLA_PORT)
    log.info("Interval: %.2fs", AUTOSWITCH_INTERVAL)

    while True:
        try:
            autoswitch_once()
        except Exception as e:
            # Final safety net: daemon must never die
            log.exception("Unexpected error in autoswitch loop: %s", e)

        time.sleep(AUTOSWITCH_INTERVAL)


# -----------------------------------------------------------------------------
# Manual execution / debugging
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    run()
