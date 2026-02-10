"""
Media Policy Handler.

Application-layer component responsible for:
- Listening to media-related events
- Delegating decision logic to the domain
- Emitting PolicyDecision events

Rules:
- No I/O
- No filesystem access
- No business rules (delegation only)
"""

from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.domain.events import (
    MediaActivityChanged,
    PolicyDecision,
)
from camilladsp_autoswitch.domain.mapping import MediaMapping
from camilladsp_autoswitch.domain.policy import (
    select_profile_for_media_state,
)


class MediaPolicyHandler:
    """
    Application adapter between media activity events and policy decisions.
    """

    def __init__(
        self,
        bus: EventBus,
        *,
        mapping: MediaMapping,
    ) -> None:
        self._bus = bus
        self._mapping = mapping

        self._bus.subscribe(
            MediaActivityChanged,
            self._on_media_activity_changed,
        )

    def _on_media_activity_changed(
        self,
        event: MediaActivityChanged,
    ) -> None:
        selection = select_profile_for_media_state(
            mapping=self._mapping,
            media_active=event.active,
        )

        decision = PolicyDecision(
            profile=selection.profile,
            variant=selection.variant,
            reason="media_active" if event.active else "media_inactive",
        )

        self._bus.publish(decision)
