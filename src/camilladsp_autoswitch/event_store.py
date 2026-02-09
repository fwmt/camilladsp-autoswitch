from typing import List, Callable, Iterable

class EventStore:
    """
    In-memory event store with replay capability.
    """

    def __init__(self):
        self._events = []

    def append(self, event):
        self._events.append(event)

    def all(self):
        return list(self._events)

    def replay(self, bus):
        for event in self._events:
            bus.publish(event)


