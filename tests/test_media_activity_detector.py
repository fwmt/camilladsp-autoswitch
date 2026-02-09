from unittest.mock import MagicMock

from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.events import MediaActivityChanged
from camilladsp_autoswitch.media_activity_detector import MediaActivityDetector


def test_detector_does_not_emit_event_on_first_poll():
    detect_fn = MagicMock(return_value=False)
    bus = EventBus()
    handler = MagicMock()

    bus.subscribe(MediaActivityChanged, handler)

    detector = MediaActivityDetector(
        detect_fn=detect_fn,
        event_bus=bus,
    )

    detector.poll()

    handler.assert_not_called()


def test_detector_emits_event_when_media_becomes_active():
    states = [False, True]
    detect_fn = MagicMock(side_effect=states)

    bus = EventBus()
    handler = MagicMock()
    bus.subscribe(MediaActivityChanged, handler)

    detector = MediaActivityDetector(
        detect_fn=detect_fn,
        event_bus=bus,
    )

    detector.poll()  # initial state
    detector.poll()  # change

    handler.assert_called_once_with(
        MediaActivityChanged(active=True)
    )


def test_detector_emits_event_when_media_becomes_inactive():
    states = [True, False]
    detect_fn = MagicMock(side_effect=states)

    bus = EventBus()
    handler = MagicMock()
    bus.subscribe(MediaActivityChanged, handler)

    detector = MediaActivityDetector(
        detect_fn=detect_fn,
        event_bus=bus,
    )

    detector.poll()  # initial state
    detector.poll()  # change

    handler.assert_called_once_with(
        MediaActivityChanged(active=False)
    )


def test_detector_does_not_emit_event_when_state_is_stable():
    detect_fn = MagicMock(return_value=True)

    bus = EventBus()
    handler = MagicMock()
    bus.subscribe(MediaActivityChanged, handler)

    detector = MediaActivityDetector(
        detect_fn=detect_fn,
        event_bus=bus,
    )

    detector.poll()
    detector.poll()
    detector.poll()

    handler.assert_not_called()
