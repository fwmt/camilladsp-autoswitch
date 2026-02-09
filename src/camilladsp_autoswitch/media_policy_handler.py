"""
Media Policy Handler.

Application-layer component responsible for:
- Listening to media-related events
- Applying policy rules
- Emitting PolicyDecision objects

Rules:
- No I/O
- No filesystem access
- No CamillaDSP access
- Pure decision logic
"""

from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.events import MediaActivityChanged
from camilladsp_autoswitch.policy import (
    PolicyDecision,
    media_player_policy,
    map_decision_to_profile,
)


class MediaPolicyHandler:
    """
    Handles media activity events and produces policy decisions.

    This handler represents the **decision boundary**
    between detection and execution.
    """

    def __init__(self, bus: EventBus):
        self._bus = bus

        # Subscribe to media activity events
        self._bus.subscribe(
            MediaActivityChanged,
            self._on_media_activity_changed,
        )

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_media_activity_changed(
        self,
        event: MediaActivityChanged,
    ) -> None:
        """
        React to media activity changes.

        Args:
            event:
                MediaActivityChanged event containing
                whether media is currently active.
        """

        # --------------------------------------------------------------
        # 1. Apply policy rules
        # --------------------------------------------------------------

        decision = media_player_policy(event.active)

        # --------------------------------------------------------------
        # 2. Apply environment-based profile mapping
        # --------------------------------------------------------------

        decision = map_decision_to_profile(decision)

        # --------------------------------------------------------------
        # 3. Emit decision event
        # --------------------------------------------------------------

        self._bus.publish(decision)
