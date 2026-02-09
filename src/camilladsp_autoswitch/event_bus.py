from collections import defaultdict
from typing import Type, Callable, Any


class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_type: Type, handler: Callable[[Any], None]) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event: Any) -> None:
        # dispatch only to matching types
        for event_type, handlers in self._subscribers.items():
            if isinstance(event, event_type):
                for handler in handlers:
                    handler(event)
