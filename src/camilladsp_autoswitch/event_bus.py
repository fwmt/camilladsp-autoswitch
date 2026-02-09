"""
In-process Event Bus.

Responsibilities:
- Register event handlers
- Dispatch events to interested subscribers

This is a SIMPLE synchronous event bus.
No threads, no queues, no async.

Rules:
- No business logic
- No I/O
"""

from collections import defaultdict
from typing import Callable, Dict, List, Type

from camilladsp_autoswitch.events import Event


EventHandler = Callable[[Event], None]


class EventBus:
    """
    Minimal synchronous event bus.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[Type[Event], List[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: Type[Event], handler: EventHandler) -> None:
        """
        Subscribe a handler to an event type.
        """
        self._subscribers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.

        Handlers are executed synchronously.
        """
        for event_type, handlers in self._subscribers.items():
            if isinstance(event, event_type):
                for handler in handlers:
                    handler(event)
