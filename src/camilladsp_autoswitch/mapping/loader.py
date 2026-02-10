from pathlib import Path
import logging

from camilladsp_autoswitch.config.paths import get_config_dir
from camilladsp_autoswitch.mapping.media import (
    MediaMapping,
    MappingError,
    ProfileSelection,
)

logger = logging.getLogger(__name__)

DEFAULT_MAPPING_PATH = get_config_dir() / "mapping.yml"


class MediaMappingLoadError(RuntimeError):
    """Raised when mapping is invalid and cannot be loaded."""


def default_mapping() -> MediaMapping:
    """
    Hard-safe fallback mapping.

    This mapping is GUARANTEED to work and must NEVER fail.
    """
    return MediaMapping(
        on=ProfileSelection(
            profile="cinema",
            variant=None,
        ),
        off=ProfileSelection(
            profile="music",
            variant=None,
        ),
    )


def load_media_mapping(
    path: Path | None = None,
    *,
    allow_fallback: bool = True,
) -> MediaMapping:
    """
    Load MediaMapping from disk.

    Production rules:
    - mapping.yml is OPTIONAL
    - invalid or missing mapping falls back safely
    """

    mapping_path = path or DEFAULT_MAPPING_PATH

    try:
        return MediaMapping.load(mapping_path)

    except FileNotFoundError:
        logger.warning(
            "Media mapping not found: %s — using default mapping",
            mapping_path,
        )

    except MappingError as exc:
        logger.error(
            "Invalid media mapping at %s — %s",
            mapping_path,
            exc,
        )

    if allow_fallback:
        return default_mapping()

    raise MediaMappingLoadError(
        f"Invalid media mapping: {mapping_path}"
    )
