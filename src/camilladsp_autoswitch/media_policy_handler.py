"""
Public re-export for MediaPolicyHandler.

This module exists to preserve backward compatibility
while the internal architecture follows Clean Architecture.
"""

from camilladsp_autoswitch.application.handlers.media_policy_handler import (
    MediaPolicyHandler,
)

__all__ = ["MediaPolicyHandler"]
