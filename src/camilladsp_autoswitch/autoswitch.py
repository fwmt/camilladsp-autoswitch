"""
CamillaDSP Autoswitch daemon.

Application service:
- orchestrates detection, policy, intent, mapping and execution
- contains NO business rules
"""

from pathlib import Path
import logging
import os
import time

from camilladsp_autoswitch.flags import load_state
from camilladsp_autoswitch.validator import validate
from camilladsp_autoswitch.policy import (
    media_player_policy,
    PolicyDecision,
    map_decision_to_profile,
)
from camilladsp_autoswitch.intent import build_intent_from_policy
from camilladsp_autoswitch.mapping import resolve_yaml_path as _resolve_yaml_path
from camilladsp_autoswitch.detectors.process import is_process_running
from camilladsp_autoswitch.executor import IntentExecutor

# Optional dependency
try:
    from camilladsp import CamillaDSP
except ImportError:
    CamillaDSP = None


# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------

LOG_LEVEL = os.environ.get("CDSP_LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [autoswitch] %(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Environment
# ------------------------------------------------------------------

CONFIG_BASE_DIR = Path(
    os.environ.get("CDSP_CONFIG_DIR", "/etc/camilladsp")
)

AUTOSWITCH_INTERVAL = float(
    os.environ.get("CDSP_AUTOSWITCH_INTERVAL", "2.0")
)

CAMILLA_HOST = os.environ.get("CDSP_CAMILLA_HOST", "127.0.0.1")
CAMILLA_PORT = int(os.environ.get("CDSP_CAMILLA_PORT", "1234"))

MEDIA_PROCESS_NAMES = ["kodi"]


# ------------------------------------------------------------------
# CamillaDSP interaction
# ------------------------------------------------------------------

def apply_yaml(yaml_path: Path) -> None:
    if CamillaDSP is None:
        return

    try:
        client = CamillaDSP(host=CAMILLA_HOST, port=CAMILLA_PORT)
        client.set_config_name(str(yaml_path))
        client.reload()
    except Exception as exc:
        logger.error("Failed to apply config: %s", exc)


# ------------------------------------------------------------------
# Executor wiring
# ------------------------------------------------------------------

_executor = IntentExecutor(
    validate_fn=validate,
    apply_fn=apply_yaml,
)


def _reset_internal_state() -> None:
    """
    Test-only reset hook (required by legacy tests).
    """
    _executor.reset()
    _executor.configure(
        validate_fn=validate,
        apply_fn=apply_yaml,
    )


# ------------------------------------------------------------------
# Detection
# ------------------------------------------------------------------

def detect_media_activity() -> bool:
    return any(
        is_process_running(name)
        for name in MEDIA_PROCESS_NAMES
    )


# ------------------------------------------------------------------
# Legacy adapter (tests expect this!)
# ------------------------------------------------------------------

def resolve_yaml_path(state):
    """
    Backward compatibility adapter.

    Accepts CDSPState and delegates to mapping layer.
    """
    decision = PolicyDecision(
        profile=state.profile,
        variant=state.variant,
        reason="legacy",
    )
    return _resolve_yaml_path(
        decision=decision,
        config_dir=CONFIG_BASE_DIR,
        experimental_yml=state.experimental_yml,
    )


# ------------------------------------------------------------------
# Core loop
# ------------------------------------------------------------------

def autoswitch_once() -> None:
    state = load_state()
    media_active = detect_media_activity()

    if state.mode == "manual":
        decision = PolicyDecision(
            profile=state.profile,
            variant=state.variant,
            reason="manual_mode",
        )
    else:
        decision = media_player_policy(media_active)

    decision = map_decision_to_profile(decision)
    intent = build_intent_from_policy(decision)

    yaml_path = _resolve_yaml_path(
        decision=decision,
        config_dir=CONFIG_BASE_DIR,
        experimental_yml=state.experimental_yml,
    )

    _executor.execute(intent, yaml_path)


def run() -> None:
    _reset_internal_state()

    while True:
        try:
            autoswitch_once()
        except Exception:
            logger.exception("Autoswitch error")
        time.sleep(AUTOSWITCH_INTERVAL)
