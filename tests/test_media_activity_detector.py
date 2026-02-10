from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.infrastructure.detectors.media_activity_detector import MediaActivityDetector
from camilladsp_autoswitch.domain.events import ProcessStarted, MediaActivityChanged

def test_emits_active_on_media_process_start():
    bus = EventBus()
    received = []

    bus.subscribe(MediaActivityChanged, lambda e: received.append(e))

    MediaActivityDetector(bus, media_processes=["kodi"])

    bus.publish(ProcessStarted(name="kodi"))

    assert len(received) == 1
    assert received[0].active is True

from camilladsp_autoswitch.domain.events import ProcessStopped

def test_emits_inactive_on_media_process_stop():
    bus = EventBus()
    received = []

    bus.subscribe(MediaActivityChanged, lambda e: received.append(e))

    MediaActivityDetector(bus, media_processes=["kodi"])

    bus.publish(ProcessStarted(name="kodi"))
    bus.publish(ProcessStopped(name="kodi"))

    assert received[-1].active is False

def test_ignores_unrelated_process():
    bus = EventBus()
    received = []

    bus.subscribe(MediaActivityChanged, lambda e: received.append(e))

    MediaActivityDetector(bus, media_processes=["kodi"])

    bus.publish(ProcessStarted(name="bash"))

    assert received == []
