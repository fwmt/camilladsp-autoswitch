from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.infrastructure.eventing.event_recorder import EventRecorder
from camilladsp_autoswitch.domain.events import MediaActivityChanged


def test_event_recorder_records_events():
    bus = EventBus()
    recorder = EventRecorder(bus)

    bus.publish(MediaActivityChanged(active=True))

    events = recorder.all()

    assert len(events) == 1
    assert isinstance(events[0], MediaActivityChanged)

def test_event_recorder_preserves_order():
    bus = EventBus()
    recorder = EventRecorder(bus)

    bus.publish(MediaActivityChanged(active=False))
    bus.publish(MediaActivityChanged(active=True))

    events = recorder.all()

    assert events[0].active is False
    assert events[1].active is True

def test_event_recorder_clear():
    bus = EventBus()
    recorder = EventRecorder(bus)

    bus.publish(MediaActivityChanged(active=True))
    recorder.clear()

    assert recorder.all() == []
