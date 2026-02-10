"""
Domain policy rules.

Pure decision logic.
No I/O. No side effects.
"""

from camilladsp_autoswitch.domain.mapping import MediaMapping, ProfileSelection


def select_profile_for_media_state(
    *,
    mapping: MediaMapping,
    media_active: bool,
) -> ProfileSelection:
    """
    Decide which profile should be used based on media activity.

    This function is PURE:
    - no filesystem
    - no events
    - no bus
    """
    return mapping.select(media_active)
