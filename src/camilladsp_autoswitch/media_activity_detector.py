"""
Media Activity Detector.

Responsibilities:
- Observe current media activity (boolean)
- Detect state transitions
- Emit domain events via EventBus

Rules:
- No policy
- No autoswitch logic
- No filesystem
- No CamillaDSP
"""

from typing import Callable, Optional

from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.events import MediaActivityChanged


class MediaActivityDetector:
    """
    Detects changes in media activity and emits events.
    """

    def __init__(
        self,
        *,
        detect_fn: Callable[[], bool],
        event_bus: EventBus,
    ) -> None:
        """
        Args:
            detect_fn:
                Function that returns True if media is active.
            event_bus:
                Event bus used to publish domain events.
        """
        self._detect_fn = detect_fn
        self._event_bus = event_bus
        self._last_state: Optional[bool] = None

    def poll(self) -> None:
        """
        Poll current media activity and emit event if state changed.
        """
        current_state = self._detect_fn()

        # First run: initialize state, no event
        if self._last_state is None:
            self._last_state = current_state
            return

        # State changed → emit event
        if current_state != self._last_state:
            self._last_state = current_state
            self._event_bus.publish(
                MediaActivityChanged(active=current_state)
            )
