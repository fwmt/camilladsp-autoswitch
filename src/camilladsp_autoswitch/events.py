"""
Public API for domain events.
"""

from camilladsp_autoswitch.domain.events import (
    Event,
    MediaActivityChanged,
    PolicyDecision,
    SwitchIntent,
    ProcessStarted,
    ProcessStopped,
)

__all__ = [
    "Event",
    "MediaActivityChanged",
    "PolicyDecision",
    "SwitchIntent",
    "ProcessStarted",
    "ProcessStopped",
]
