from camilladsp_autoswitch.events import Event


class EventRecorder:
    """
    Records all events for audit and replay.
    """

    def __init__(self, bus):
        self._events: list[Event] = []
        bus.subscribe(Event, self._record)

    def _record(self, event: Event) -> None:
        self._events.append(event)

    def all(self) -> list[Event]:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()
