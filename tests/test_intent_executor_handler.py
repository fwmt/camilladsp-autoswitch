from unittest.mock import MagicMock
from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.intent import SwitchIntent
from camilladsp_autoswitch.intent_executor_handler import IntentExecutorHandler


def test_executor_handler_applies_valid_intent():
    bus = EventBus()

    resolver = MagicMock(return_value="/tmp/music.yml")

    validator = MagicMock()
    validator.return_value.valid = True
    validator.return_value.reason = None

    applier = MagicMock()

    IntentExecutorHandler(
        bus=bus,
        resolve_yaml=resolver,
        validate=validator,
        apply=applier,
    )

    bus.publish(
        SwitchIntent(
            profile="music",
            variant=None,
            reason="test",
        )
    )

    applier.assert_called_once_with("/tmp/music.yml")

def test_executor_handler_does_not_apply_invalid_yaml():
    bus = EventBus()

    resolver = MagicMock(return_value="/tmp/broken.yml")

    validator = MagicMock()
    validator.return_value.valid = False
    validator.return_value.reason = "invalid"

    applier = MagicMock()

    IntentExecutorHandler(
        bus=bus,
        resolve_yaml=resolver,
        validate=validator,
        apply=applier,
    )

    bus.publish(
        SwitchIntent(
            profile="music",
            variant=None,
            reason="test",
        )
    )

    applier.assert_not_called()

def test_executor_handler_is_idempotent():
    bus = EventBus()

    resolver = MagicMock(return_value="/tmp/music.yml")

    validator = MagicMock()
    validator.return_value.valid = True
    validator.return_value.reason = None

    applier = MagicMock()

    IntentExecutorHandler(
        bus=bus,
        resolve_yaml=resolver,
        validate=validator,
        apply=applier,
    )

    intent = SwitchIntent(
        profile="music",
        variant=None,
        reason="test",
    )

    bus.publish(intent)
    bus.publish(intent)

    applier.assert_called_once()
