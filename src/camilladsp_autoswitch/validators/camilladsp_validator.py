import subprocess
from pathlib import Path

from camilladsp_autoswitch.registry.errors import InvalidYamlError


class CamillaDSPBinaryValidator:
    """
    Validate CamillaDSP YAML configs using the official camilladsp binary.

    This validator delegates validation to:
        camilladsp --check <config.yml>

    Design goals:
    - Use the same validation logic as production
    - No YAML parsing or schema reimplementation
    - Fail fast with clear error messages
    """

    def __init__(self, binary: str = "camilladsp"):
        self._binary = binary

    def validate(self, path: Path) -> None:
        path = Path(path)

        if not path.exists():
            raise InvalidYamlError(f"YAML file not found: {path}")

        try:
            result = subprocess.run(
                [self._binary, "--check", str(path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
        except FileNotFoundError as exc:
            raise InvalidYamlError(
                f"CamillaDSP binary not found: {self._binary}"
            ) from exc

        if result.returncode != 0:
            output = "\n".join(
                line for line in [
            	    result.stderr.strip(),
            	    result.stdout.strip(),
        	]
                if line
            )

            raise InvalidYamlError(
                "CamillaDSP rejected the configuration.\n"
                "Output:\n"
                f"{output or '(no detailed error message)'}"
            )

