from camilladsp_autoswitch.event_store import EventStore


def test_event_store_records_events():
    store = EventStore()

    store.append("a")
    store.append("b")

    assert store.all() == ["a", "b"]
