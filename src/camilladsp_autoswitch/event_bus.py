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
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, handler):
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event):
        """
        API pública (observável / interceptável em testes)
        """
        self._emit(event)

    def _emit(self, event):
        """
        Núcleo interno do EventBus.
        Nunca deve ser sobrescrito.
        """
        for event_type, handlers in self._subscribers.items():
            if isinstance(event, event_type):
                for handler in handlers:
                    handler(event)
