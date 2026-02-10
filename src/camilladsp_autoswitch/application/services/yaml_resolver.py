from pathlib import Path
from camilladsp_autoswitch.domain.events import PolicyDecision


def resolve_yaml_path(
    *,
    decision: PolicyDecision,
    config_dir: Path,
    experimental_yml: str | None,
) -> Path:
    """
    Resolve the concrete YAML path for a policy decision.
    """
    if experimental_yml:
        return Path(experimental_yml)

    if decision.variant:
        return config_dir / f"{decision.profile}.{decision.variant}.yml"

    return config_dir / f"{decision.profile}.yml"
