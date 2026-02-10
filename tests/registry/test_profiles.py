import pytest
from pathlib import Path

from camilladsp_autoswitch.registry.profiles import ProfileRegistry
from camilladsp_autoswitch.registry.errors import (
    InvalidYamlError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)


# ---------------------------------------------------------------------
# Fake validators (injeção de dependência)
# ---------------------------------------------------------------------

class AlwaysValidValidator:
    def validate(self, path: Path) -> None:
        return None


class AlwaysInvalidValidator:
    def validate(self, path: Path) -> None:
        raise InvalidYamlError(f"Invalid YAML: {path}")


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def write_yaml(path: Path, content: str = "dummy") -> Path:
    path.write_text(content)
    return path


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------

def test_add_valid_profile(tmp_path):
    config_dir = tmp_path / "config"
    source = write_yaml(tmp_path / "music.yml")

    registry = ProfileRegistry(
        config_dir,
        validator=AlwaysValidValidator(),
    )

    registry.add(
        name="music",
        source_path=source,
    )

    stored = config_dir / "profiles" / "music.yml"
    assert stored.exists()
    assert stored.read_text() == "dummy"


def test_add_valid_profile_with_variant(tmp_path):
    config_dir = tmp_path / "config"
    source = write_yaml(tmp_path / "cinema.yml")

    registry = ProfileRegistry(
        config_dir,
        validator=AlwaysValidValidator(),
    )

    registry.add(
        name="cinema",
        variant="night",
        source_path=source,
    )

    stored = config_dir / "profiles" / "cinema.night.yml"
    assert stored.exists()


def test_reject_invalid_yaml_via_validator(tmp_path):
    config_dir = tmp_path / "config"
    source = write_yaml(tmp_path / "bad.yml")

    registry = ProfileRegistry(
        config_dir,
        validator=AlwaysInvalidValidator(),
    )

    with pytest.raises(InvalidYamlError):
        registry.add(
            name="broken",
            source_path=source,
        )


def test_resolve_profile_without_variant(tmp_path):
    config_dir = tmp_path / "config"
    source = write_yaml(tmp_path / "music.yml")

    registry = ProfileRegistry(
        config_dir,
        validator=AlwaysValidValidator(),
    )
    registry.add(name="music", source_path=source)

    resolved = registry.resolve("music")
    assert resolved.name == "music.yml"
    assert resolved.exists()


def test_resolve_profile_with_variant(tmp_path):
    config_dir = tmp_path / "config"
    source = write_yaml(tmp_path / "cinema.yml")

    registry = ProfileRegistry(
        config_dir,
        validator=AlwaysValidValidator(),
    )
    registry.add(name="cinema", variant="night", source_path=source)

    resolved = registry.resolve("cinema", variant="night")
    assert resolved.name == "cinema.night.yml"


def test_resolve_missing_profile_raises(tmp_path):
    registry = ProfileRegistry(
        tmp_path / "config",
        validator=AlwaysValidValidator(),
    )

    with pytest.raises(ProfileNotFoundError):
        registry.resolve("nonexistent")


def test_duplicate_profile_requires_force(tmp_path):
    config_dir = tmp_path / "config"
    source1 = write_yaml(tmp_path / "music.yml", "one")
    source2 = write_yaml(tmp_path / "music2.yml", "two")

    registry = ProfileRegistry(
        config_dir,
        validator=AlwaysValidValidator(),
    )
    registry.add(name="music", source_path=source1)

    with pytest.raises(ProfileAlreadyExistsError):
        registry.add(name="music", source_path=source2)

    # With force=True it must overwrite
    registry.add(
        name="music",
        source_path=source2,
        force=True,
    )

    stored = config_dir / "profiles" / "music.yml"
    assert stored.read_text() == "two"
