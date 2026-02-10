from pathlib import Path

from camilladsp_autoswitch.domain.mapping import MediaMapping, MappingError
from camilladsp_autoswitch.config.paths import get_config_dir


# ------------------------------------------------------------------
# Default path (RESPEITA CDSP_CONFIG_DIR)
# ------------------------------------------------------------------

DEFAULT_MAPPING_PATH = get_config_dir() / "mapping.yml"


# ------------------------------------------------------------------
# Loader
# ------------------------------------------------------------------

class MediaMappingLoadError(Exception):
    """Raised when media mapping cannot be loaded."""


def load_media_mapping(path: Path | None = None) -> MediaMapping:
    """
    Load MediaMapping from disk.

    Rules:
    - Path must exist
    - Mapping must be valid
    - Fail fast and loudly on error
    """

    mapping_path = path or DEFAULT_MAPPING_PATH

    try:
        return MediaMapping.load(mapping_path)
    except MappingError as exc:
        raise MediaMappingLoadError(
            f"Invalid media mapping: {mapping_path}"
        ) from exc
