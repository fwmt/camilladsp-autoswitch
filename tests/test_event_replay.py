from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.event_store import EventStore
from camilladsp_autoswitch.event_store_subscriber import EventStoreSubscriber
from camilladsp_autoswitch.domain.events import MediaActivityChanged


def test_event_replay_reconstructs_state():
    bus = EventBus()
    store = EventStore()
    EventStoreSubscriber(bus, store)

    # simula eventos passados
    bus.publish(MediaActivityChanged(active=True))
    bus.publish(MediaActivityChanged(active=False))

    # novo bus "reconstruído"
    replay_bus = EventBus()
    received = []

    replay_bus.subscribe(MediaActivityChanged, lambda e: received.append(e))

    store.replay(replay_bus)

    assert len(received) == 2
    assert received[0].active is True
    assert received[1].active is False
