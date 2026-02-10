from pathlib import Path

from camilladsp_autoswitch.mapping.media import MediaMapping, MappingError


DEFAULT_MAPPING_PATH = Path("/etc/camilladsp-autoswitch/mapping.yml")


class MediaMappingLoadError(RuntimeError):
    """Raised when media mapping cannot be loaded."""


def load_media_mapping(
    path: Path | None = None,
) -> MediaMapping:
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
