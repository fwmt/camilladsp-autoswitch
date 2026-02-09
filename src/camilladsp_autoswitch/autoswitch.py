"""
CamillaDSP Autoswitch daemon.

Responsabilidade:
- Adaptador LEGADO para testes antigos
- Funções utilitárias ainda referenciadas por testes
- NÃO contém lógica de negócio nova
"""

from pathlib import Path
import logging
import os

from camilladsp_autoswitch.flags import load_state
from camilladsp_autoswitch.policy import (
    PolicyDecision,
    media_player_policy,
    map_decision_to_profile,
)
from camilladsp_autoswitch.intent import build_intent_from_policy
from camilladsp_autoswitch.mapping import resolve_yaml_path
from camilladsp_autoswitch.executor import IntentExecutor
from camilladsp_autoswitch.validator import validate

# 🔴 IMPORTANTE PARA OS TESTES
# Reexport explícito para permitir:
# @patch("camilladsp_autoswitch.autoswitch.is_process_running")
from camilladsp_autoswitch.detectors.process import is_process_running


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

MEDIA_PROCESS_NAMES = ["kodi"]


# ------------------------------------------------------------------
# CamillaDSP interaction (LEGADO)
# ------------------------------------------------------------------

try:
    from camilladsp import CamillaDSP
except ImportError:
    CamillaDSP = None


def apply_yaml(yaml_path: Path) -> None:
    """
    LEGACY executor hook.
    Mantido apenas para compatibilidade.
    """
    if CamillaDSP is None:
        return

    try:
        client = CamillaDSP(host="127.0.0.1", port=1234)
        client.set_config_name(str(yaml_path))
        client.reload()
    except Exception as exc:
        logger.error("Failed to apply config: %s", exc)


# ------------------------------------------------------------------
# Detection (LEGADO)
# ------------------------------------------------------------------

def detect_media_activity() -> bool:
    """
    Função LEGADA usada por testes antigos.

    ⚠️ IMPORTANTE:
    Usa o símbolo `is_process_running` LOCAL,
    para permitir patch correto nos testes.
    """
    return any(
        is_process_running(name)
        for name in MEDIA_PROCESS_NAMES
    )


# ------------------------------------------------------------------
# Executor (LEGADO)
# ------------------------------------------------------------------

_executor = IntentExecutor(
    validate_fn=validate,
    apply_fn=apply_yaml,
)


def _reset_internal_state() -> None:
    """
    Hook exigido por testes antigos.
    """
    _executor.reset()
    _executor.configure(
        validate_fn=validate,
        apply_fn=apply_yaml,
    )


# ------------------------------------------------------------------
# Core loop (LEGADO)
# ------------------------------------------------------------------

def autoswitch_once() -> None:
    """
    Loop antigo — mantido apenas para compatibilidade.
    O novo sistema é event-driven.
    """
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

    yaml_path = resolve_yaml_path(
        decision=decision,
        config_dir=CONFIG_BASE_DIR,
        experimental_yml=state.experimental_yml,
    )

    _executor.execute(intent, yaml_path)
