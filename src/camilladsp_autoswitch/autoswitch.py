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
from camilladsp_autoswitch.detectors.process import is_process_running

# Optional dependency: pycamilladsp
# The daemon MUST keep running even if this is not installed.
try:
    from camilladsp import CamillaDSP
except ImportError:
    CamillaDSP = None

logger = logging.getLogger(__name__)

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
MEDIA_PROCESS_NAMES = [
    "kodi",
]


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

def _reset_internal_state():
    """
    Reset internal autoswitch state.

    This function exists to:
    - support unit testing
    - allow clean daemon restarts
    """
    global _last_yaml, _last_validation_ok
    _last_yaml = None
    _last_validation_ok = None


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

def detect_media_activity() -> bool:
    """
    Detect whether any known media application is currently active.

    Returns:
        True if at least one configured media process is running.
    """
    for process_name in MEDIA_PROCESS_NAMES:
        if is_process_running(process_name):
            return True
    return False

def decide_profile(
    *,
    state,
    media_active: bool,
) -> str:
    """
    Decide which profile should be active based on the current state
    and detected media activity.

    Rules (automatic mode only):
    - If media is active: use 'cinema'
    - If media is inactive: use 'music'

    Manual mode always preserves the user-selected profile.

    Args:
        state: Current CDSPState
        media_active: Whether media activity is detected

    Returns:
        Profile name to use ('music' or 'cinema')
    """
    if state.mode == "manual":
        return state.profile

    if media_active:
        return "cinema"

    return "music"


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
    media_active = detect_media_activity()

    effective_profile = decide_profile(
        state=state,
        media_active=media_active,
    )

    # Create a derived state for resolution only
    effective_state = state
    effective_state.profile = effective_profile

    yaml_path = resolve_yaml_path(effective_state)


    yaml_changed = yaml_path != _last_yaml

    result = validate(yaml_path)

    media_active = detect_media_activity()

    logger.info(
        "Media activity detected: %s",
        "active" if media_active else "inactive",
    )


    if not result.valid:
        if yaml_changed or _last_validation_ok is not False:
            log.error("YAML invalid: %s", result.reason)
        _last_yaml = yaml_path
        _last_validation_ok = False
        return

    if yaml_changed or _last_validation_ok is not True:
        log.info("YAML validated: %s", yaml_path)

    # 🔑 IMPORTANT FIX:
    # Apply once on first valid run, then only on changes
    if _last_yaml is None or yaml_changed:
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

    # Ensure clean state on daemon start
    _reset_internal_state()

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
