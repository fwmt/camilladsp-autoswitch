from pathlib import Path
from camilladsp_autoswitch.policy import PolicyDecision


def resolve_yaml_path(
    *,
    decision: PolicyDecision,
    config_dir: Path,
    experimental_yml: str | None = None,
) -> Path:
    """
    Resolve YAML path from a PolicyDecision.

    No I/O, no validation, no DSP.
    """

    if experimental_yml:
        return Path(experimental_yml)

    name = decision.profile

    if decision.variant and decision.variant != "normal":
        name = f"{name}_{decision.variant}"

    return config_dir / f"{name}.yml"
