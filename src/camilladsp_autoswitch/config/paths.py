import os
from pathlib import Path


def get_config_dir() -> Path:
    """
    Return base configuration directory.

    Production:
        /etc/camilladsp-autoswitch

    Development:
        override with CDSP_CONFIG_DIR
    """
    return Path(
        os.environ.get(
            "CDSP_CONFIG_DIR",
            "/etc/camilladsp-autoswitch",
        )
    )
