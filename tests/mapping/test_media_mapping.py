import pytest
from pathlib import Path

from camilladsp_autoswitch.mapping.media import (
    MediaMapping,
    MappingError,
)


VALID_MAPPING = """
media:
  off:
    profile: music
    variant: normal

  on:
    profile: cinema
    variant: night
"""

MINIMAL_MAPPING = """
media:
  off:
    profile: music

  on:
    profile: cinema
"""

INVALID_NO_MEDIA = """
off:
  profile: music
"""

INVALID_NO_ON = """
media:
  off:
    profile: music
"""

INVALID_NO_PROFILE = """
media:
  off:
    variant: normal
  on:
    profile: cinema
"""


def write_mapping(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "mapping.yml"
    path.write_text(content)
    return path


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

def test_load_valid_mapping(tmp_path):
    path = write_mapping(tmp_path, VALID_MAPPING)

    mapping = MediaMapping.load(path)

    assert mapping.off.profile == "music"
    assert mapping.off.variant == "normal"
    assert mapping.on.profile == "cinema"
    assert mapping.on.variant == "night"


def test_load_minimal_mapping(tmp_path):
    path = write_mapping(tmp_path, MINIMAL_MAPPING)

    mapping = MediaMapping.load(path)

    assert mapping.off.profile == "music"
    assert mapping.off.variant is None
    assert mapping.on.profile == "cinema"
    assert mapping.on.variant is None


def test_missing_media_section(tmp_path):
    path = write_mapping(tmp_path, INVALID_NO_MEDIA)

    with pytest.raises(MappingError):
        MediaMapping.load(path)


def test_missing_on_section(tmp_path):
    path = write_mapping(tmp_path, INVALID_NO_ON)

    with pytest.raises(MappingError):
        MediaMapping.load(path)


def test_missing_profile_in_off(tmp_path):
    path = write_mapping(tmp_path, INVALID_NO_PROFILE)

    with pytest.raises(MappingError):
        MediaMapping.load(path)


def test_select_profile_when_media_on(tmp_path):
    path = write_mapping(tmp_path, VALID_MAPPING)
    mapping = MediaMapping.load(path)

    selected = mapping.select(media_active=True)

    assert selected.profile == "cinema"
    assert selected.variant == "night"


def test_select_profile_when_media_off(tmp_path):
    path = write_mapping(tmp_path, VALID_MAPPING)
    mapping = MediaMapping.load(path)

    selected = mapping.select(media_active=False)

    assert selected.profile == "music"
    assert selected.variant == "normal"
