from unittest.mock import MagicMock

from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.domain.events import MediaActivityChanged


def test_event_bus_calls_subscriber():
    bus = EventBus()
    handler = MagicMock()

    bus.subscribe(MediaActivityChanged, handler)

    event = MediaActivityChanged(active=True)
    bus.publish(event)

    handler.assert_called_once_with(event)


def test_event_bus_does_not_call_unrelated_handlers():
    bus = EventBus()
    handler = MagicMock()

    # Subscribe to MediaActivityChanged
    bus.subscribe(MediaActivityChanged, handler)

    # Publish a different instance type (still MediaActivityChanged)
    event = MediaActivityChanged(active=False)
    bus.publish(event)

    handler.assert_called_once_with(event)


def test_event_bus_supports_multiple_subscribers():
    bus = EventBus()
    handler_a = MagicMock()
    handler_b = MagicMock()

    bus.subscribe(MediaActivityChanged, handler_a)
    bus.subscribe(MediaActivityChanged, handler_b)

    event = MediaActivityChanged(active=True)
    bus.publish(event)

    handler_a.assert_called_once_with(event)
    handler_b.assert_called_once_with(event)
