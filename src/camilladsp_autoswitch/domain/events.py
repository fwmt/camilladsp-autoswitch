from dataclasses import dataclass


class Event:
    """Base marker class"""
    pass


@dataclass(frozen=True)
class MediaActivityChanged(Event):
    active: bool


@dataclass(frozen=True)
class PolicyDecision(Event):
    profile: str
    variant: str | None
    reason: str


@dataclass(frozen=True)
class SwitchIntent(Event):
    profile: str
    variant: str | None
    reason: str

@dataclass(frozen=True)
class ProcessStarted:
    name: str


@dataclass(frozen=True)
class ProcessStopped:
    name: str
