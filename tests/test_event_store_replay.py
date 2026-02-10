from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.infrastructure.eventing.event_store import EventStore


def test_event_store_replay():
    store = EventStore()

    store.append("event1")
    store.append("event2")

    bus = EventBus()
    publish = []

    bus.publish = lambda e: publish.append(e)

    store.replay(bus)

    assert "event1" in publish
    assert "event2" in publish
