from unittest.mock import MagicMock

from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.logging_subscriber import LoggingSubscriber
from camilladsp_autoswitch.domain.events import MediaActivityChanged


def test_logging_subscriber_logs_event():
    bus = EventBus()
    logger = MagicMock()

    LoggingSubscriber(bus, logger=logger)

    bus.publish(MediaActivityChanged(active=True))

    logger.info.assert_called_once()


def test_logging_contains_event_name():
    bus = EventBus()
    logger = MagicMock()

    LoggingSubscriber(bus, logger=logger)

    bus.publish(MediaActivityChanged(active=False))

    args, _ = logger.info.call_args
    assert logger.info.called
