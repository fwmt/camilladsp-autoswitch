"""
Domain Events.

All events emitted by the system must inherit from Event.
"""

from dataclasses import dataclass


class Event:
    """
    Base class for all domain events.

    This class is intentionally minimal.
    It exists to:
    - provide a common type
    - support EventBus typing
    - allow future metadata extension
    """
    pass


@dataclass(frozen=True)
class MediaActivityChanged(Event):
    active: bool


@dataclass(frozen=True)
class SwitchIntentCreated(Event):
    profile: str
    variant: str | None
    reason: str
