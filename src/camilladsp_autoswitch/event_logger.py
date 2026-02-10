"""
Event logger subscriber.

Observes events flowing through the system
without affecting behavior.
"""

import logging
from camilladsp_autoswitch.domain.events import Event

logger = logging.getLogger("camilladsp_autoswitch.domain.events")


class EventLogger:
    """
    Logs every domain event published on the bus.
    """

    def __init__(self, bus):
        bus.subscribe(Event, self.handle)

    def handle(self, event: Event) -> None:
        logger.info(
            "EVENT: %s %s",
            event.__class__.__name__,
            event,
        )
