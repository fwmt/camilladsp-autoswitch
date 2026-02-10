from pathlib import Path
from typing import Optional

from camilladsp_autoswitch.registry.errors import (
    InvalidYamlError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)


class ProfileRegistry:
    """
    Registry of validated CamillaDSP YAML profiles.

    Responsibilities:
    - Validate YAML via injected validator
    - Store YAMLs in a controlled directory
    - Resolve YAMLs by (profile, variant)
    """

    def __init__(self, config_dir: Path, validator):
        self._config_dir = Path(config_dir)
        self._profiles_dir = self._config_dir / "profiles"
        self._validator = validator

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(
        self,
        *,
        name: str,
        source_path: Path,
        variant: Optional[str] = None,
        force: bool = False,
    ) -> None:
        source_path = Path(source_path)

        if not source_path.exists():
            raise InvalidYamlError(f"YAML file not found: {source_path}")

        # Delegate validation (external responsibility)
        self._validator.validate(source_path)

        self._profiles_dir.mkdir(parents=True, exist_ok=True)

        target = self._profile_path(name, variant)

        if target.exists() and not force:
            raise ProfileAlreadyExistsError(
                f"Profile already exists: {target.name}"
            )

        target.write_text(source_path.read_text())

    def resolve(self, name: str, variant: Optional[str] = None) -> Path:
        target = self._profile_path(name, variant)

        if not target.exists():
            raise ProfileNotFoundError(
                f"Profile not found: {target.name}"
            )

        return target

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _profile_path(self, name: str, variant: Optional[str]) -> Path:
        filename = name
        if variant:
            filename = f"{name}.{variant}"
        return self._profiles_dir / f"{filename}.yml"
