from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.event_store import EventStore

class EventStoreSubscriber:
    """
    Records all published events into an EventStore.
    """

    def __init__(self, bus, store):
        self._store = store
        bus.subscribe(object, self._record)

    def _record(self, event):
        self._store.append(event)
