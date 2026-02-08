"""
YAML validation for camilladsp-autoswitch.

This module validates configuration files BEFORE they are applied.
Offline validation only (no CamillaDSP dependency).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class ValidationResult:
    """
    Result of a YAML validation attempt.
    """
    valid: bool
    reason: Optional[str] = None


def validate(path: Path) -> ValidationResult:
    """
    Validate a CamillaDSP YAML configuration file.

    Rules:
    - File must exist
    - YAML must be parseable
    - Must never raise exceptions
    """

    try:
        if not path.exists():
            return ValidationResult(
                valid=False,
                reason=f"YAML file not found: {path}",
            )

        with path.open("r") as f:
            yaml.safe_load(f)

        return ValidationResult(valid=True)

    except yaml.YAMLError as e:
        return ValidationResult(
            valid=False,
            reason=f"YAML syntax error: {e}",
        )

    except Exception as e:
        return ValidationResult(
            valid=False,
            reason=str(e),
        )
