import time
import shutil
import logging
from pathlib import Path

from camilladsp_autoswitch.flags import load_state

# Base directories
BASE_DIR = Path(__file__).resolve().parents[2]
CONFIGS_DIR = BASE_DIR / "configs"

ACTIVE_DIR = CONFIGS_DIR / "active"
STAGING_DIR = CONFIGS_DIR / "staging"
ARCHIVE_DIR = CONFIGS_DIR / "archive"

POLL_INTERVAL = 2.0  # seconds


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [autoswitch] %(levelname)s: %(message)s",
    )


def resolve_profile_yaml(state) -> Path | None:
    """
    Decide which YAML file should be active based on state.
    """
    if state.experimental_yml:
        return Path(state.experimental_yml)

    name = state.profile
    variant = state.variant

    if variant != "normal":
        return CONFIGS_DIR / f"{name}_{variant}.yml"

    return CONFIGS_DIR / f"{name}.yml"


def safe_apply_yaml(source: Path):
    """
    Apply YAML safely:
    - copy to staging
    - atomically replace active
    """
    if not source.exists():
        logging.error(f"YAML not found: {source}")
        return

    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    staging_file = STAGING_DIR / source.name
    active_file = ACTIVE_DIR / "current.yml"

    shutil.copy2(source, staging_file)

    if active_file.exists():
        archived = ARCHIVE_DIR / f"{int(time.time())}_{active_file.name}"
        shutil.move(active_file, archived)

    shutil.move(staging_file, active_file)

    logging.info(f"Applied YAML: {source.name}")


def main():
    setup_logging()
    logging.info("CamillaDSP autoswitch started")

    last_applied = None

    while True:
        state = load_state()
        target = resolve_profile_yaml(state)

        if target and target != last_applied:
            logging.info(
                f"State change detected: profile={state.profile}, "
                f"variant={state.variant}, experimental={bool(state.experimental_yml)}"
            )
            safe_apply_yaml(target)
            last_applied = target

        time.sleep(POLL_INTERVAL)
