from pathlib import Path
from unittest.mock import MagicMock

from camilladsp_autoswitch.intent import SwitchIntent
from camilladsp_autoswitch.executor import IntentExecutor


def test_executor_applies_valid_intent_once(tmp_path):
    """
    A valid intent must be applied exactly once.
    """
    yaml_path = tmp_path / "music.yml"

    validator = MagicMock()
    validator.return_value.valid = True
    validator.return_value.reason = None

    applier = MagicMock()

    executor = IntentExecutor(
        validate_fn=validator,
        apply_fn=applier,
    )

    intent = SwitchIntent(
        profile="music",
        variant=None,
        reason="test",
    )

    executor.execute(intent, yaml_path)
    executor.execute(intent, yaml_path)  # second call must NOT reapply

    applier.assert_called_once_with(yaml_path)


def test_executor_does_not_apply_invalid_yaml(tmp_path):
    """
    Invalid YAML must never be applied.
    """
    yaml_path = tmp_path / "broken.yml"

    validator = MagicMock()
    validator.return_value.valid = False
    validator.return_value.reason = "invalid"

    applier = MagicMock()

    executor = IntentExecutor(
        validate_fn=validator,
        apply_fn=applier,
    )

    intent = SwitchIntent(
        profile="music",
        variant=None,
        reason="test",
    )

    executor.execute(intent, yaml_path)

    applier.assert_not_called()


def test_executor_reapplies_when_yaml_changes(tmp_path):
    """
    A new YAML path must trigger a new apply.
    """
    yaml_a = tmp_path / "music.yml"
    yaml_b = tmp_path / "cinema.yml"

    validator = MagicMock()
    validator.return_value.valid = True
    validator.return_value.reason = None

    applier = MagicMock()

    executor = IntentExecutor(
        validate_fn=validator,
        apply_fn=applier,
    )

    intent = SwitchIntent(
        profile="music",
        variant=None,
        reason="test",
    )

    executor.execute(intent, yaml_a)
    executor.execute(intent, yaml_b)

    assert applier.call_count == 2
