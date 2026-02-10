"""
Media Policy Handler.

Application-layer component responsible for:
- Listening to media-related events
- Applying media → profile mapping
- Emitting PolicyDecision events

Rules:
- No I/O
- No filesystem access
- Pure decision logic
"""

from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.domain.events import MediaActivityChanged, PolicyDecision
from camilladsp_autoswitch.domain.mapping import MediaMapping


class MediaPolicyHandler:
    """
    Decision boundary between media detection and execution.
    """

    def __init__(
        self,
        bus: EventBus,
        *,
        mapping: MediaMapping,
    ):
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
        selection = self._mapping.select(event.active)

        decision = PolicyDecision(
            profile=selection.profile,
            variant=selection.variant,
            reason="media_active" if event.active else "media_inactive",
        )

        self._bus.publish(decision)
