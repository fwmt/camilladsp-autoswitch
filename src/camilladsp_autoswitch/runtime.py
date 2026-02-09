"""
Runtime infrastructure.

Allowed:
- OS access
- CamillaDSP
- process detection

FORBIDDEN:
- domain logic
- event wiring
"""

from pathlib import Path
import os
import logging

from camilladsp_autoswitch.detectors.process import is_process_running

try:
    from camilladsp import CamillaDSP
except ImportError:
    CamillaDSP = None


# ------------------------------------------------------------------
# Media detection (legacy-compatible)
# ------------------------------------------------------------------

MEDIA_PROCESS_NAMES = ["kodi"]


def detect_media_activity() -> bool:
    return any(
        is_process_running(name)
        for name in MEDIA_PROCESS_NAMES
    )


# ------------------------------------------------------------------
# CamillaDSP apply
# ------------------------------------------------------------------

CAMILLA_HOST = os.environ.get("CDSP_CAMILLA_HOST", "127.0.0.1")
CAMILLA_PORT = int(os.environ.get("CDSP_CAMILLA_PORT", "1234"))

logger = logging.getLogger(__name__)


def apply_yaml(yaml_path: str | Path) -> None:
    if CamillaDSP is None:
        return

    try:
        client = CamillaDSP(host=CAMILLA_HOST, port=CAMILLA_PORT)
        client.set_config_name(str(yaml_path))
        client.reload()
    except Exception as exc:
        logger.error("Failed to apply config: %s", exc)
