from pathlib import Path

from camilladsp_autoswitch.domain.mapping import MediaMapping, MappingError
from camilladsp_autoswitch.mapping.loader import DEFAULT_MAPPING_PATH


class MediaMappingService:
    """
    Application service for managing media mapping.
    """

    def __init__(self, path: Path | None = None):
        self._path = path or DEFAULT_MAPPING_PATH

    # --------------------------------------------------
    # Queries
    # --------------------------------------------------

    def load(self) -> MediaMapping:
        return MediaMapping.load(self._path)

    def show(self) -> str:
        if not self._path.exists():
            raise MappingError(f"Mapping file not found: {self._path}")
        return self._path.read_text()

    # --------------------------------------------------
    # Commands
    # --------------------------------------------------

    def init(self, force: bool = False) -> None:
        if self._path.exists() and not force:
            raise MappingError(f"Mapping already exists: {self._path}")

        self._path.parent.mkdir(parents=True, exist_ok=True)

        self._path.write_text(
            """media:
  off:
    profile: music
    variant: normal

  on:
    profile: cinema
    variant: night
"""
        )

    def validate(self) -> None:
        MediaMapping.load(self._path)

    def test(self, *, media_active: bool) -> str:
        mapping = self.load()
        selection = mapping.select(media_active=media_active)
        return f"{selection.profile}.{selection.variant or 'default'}"
