from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


# ------------------------------------------------------------------
# Errors
# ------------------------------------------------------------------

class MappingError(Exception):
    """Raised when the media mapping is invalid."""


# ------------------------------------------------------------------
# Data models
# ------------------------------------------------------------------

@dataclass(frozen=True)
class ProfileSelection:
    """
    Concrete profile selection produced by a mapping decision.
    """
    profile: str
    variant: Optional[str] = None


# ------------------------------------------------------------------
# Media Mapping (Domain)
# ------------------------------------------------------------------

class MediaMapping:
    """
    Declarative mapping between media activity state and profile selection.

    PURE domain object:
    - Deterministic
    - No I/O outside load()
    - No environment access
    """

    def __init__(self, *, on: ProfileSelection, off: ProfileSelection):
        self._on = on
        self._off = off

    # --------------------------------------------------------------
    # Public read-only accessors (API compatibility)
    # --------------------------------------------------------------

    @property
    def on(self) -> ProfileSelection:
        return self._on

    @property
    def off(self) -> ProfileSelection:
        return self._off

    # --------------------------------------------------------------
    # Factory
    # --------------------------------------------------------------

    @classmethod
    def load(cls, path: Path) -> "MediaMapping":
        """
        Load MediaMapping from a YAML file.

        Expected format:

        media:
          on:
            profile: cinema
            variant: night
          off:
            profile: music
            variant: normal
        """
        path = Path(path)

        if not path.exists():
            raise MappingError(f"Mapping file not found: {path}")

        try:
            data = yaml.safe_load(path.read_text())
        except Exception as exc:
            raise MappingError("Failed to parse mapping YAML") from exc

        if not isinstance(data, dict) or "media" not in data:
            raise MappingError("Missing 'media' section")

        media_raw = data["media"]

        if not isinstance(media_raw, dict):
            raise MappingError("'media' section must be a mapping")

        # Normalize YAML boolean keys (on/off → True/False)
        media: dict[str, dict] = {}
        for key, value in media_raw.items():
            if key is True:
                media["on"] = value
            elif key is False:
                media["off"] = value
            else:
                media[str(key)] = value

        try:
            on = cls._parse_side(media, "on")
            off = cls._parse_side(media, "off")
        except KeyError as exc:
            raise MappingError(f"Missing required section: {exc}") from exc

        return cls(on=on, off=off)

    # --------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------

    def select(self, media_active: bool) -> ProfileSelection:
        """
        Select profile based on media activity state.
        """
        return self._on if media_active else self._off

    # --------------------------------------------------------------
    # Internals
    # --------------------------------------------------------------

    @staticmethod
    def _parse_side(media: dict, key: str) -> ProfileSelection:
        if key not in media:
            raise KeyError(key)

        section = media[key]

        if not isinstance(section, dict):
            raise MappingError(f"Invalid '{key}' section (must be a mapping)")

        if "profile" not in section:
            raise MappingError(f"Missing 'profile' in '{key}' section")

        profile = section["profile"]
        variant = section.get("variant")

        if not isinstance(profile, str):
            raise MappingError(f"'profile' in '{key}' section must be a string")

        if variant is not None and not isinstance(variant, str):
            raise MappingError(f"'variant' in '{key}' section must be a string")

        return ProfileSelection(
            profile=profile,
            variant=variant,
        )
