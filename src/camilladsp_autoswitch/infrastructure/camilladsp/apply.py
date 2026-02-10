from pathlib import Path
import logging
import os

try:
    from camilladsp import CamillaDSP
except ImportError:
    CamillaDSP = None

CAMILLA_HOST = os.environ.get("CDSP_CAMILLA_HOST", "127.0.0.1")
CAMILLA_PORT = int(os.environ.get("CDSP_CAMILLA_PORT", "1234"))

logger = logging.getLogger(__name__)

def apply_yaml(yaml_path: Path) -> None:
    if CamillaDSP is None:
        return
    try:
        client = CamillaDSP(host=CAMILLA_HOST, port=CAMILLA_PORT)
        client.set_config_name(str(yaml_path))
        client.reload()
    except Exception as exc:
        logger.error("Failed to apply config: %s", exc)
