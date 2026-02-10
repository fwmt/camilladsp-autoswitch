"""
camilladsp-autoswitch public API
"""

# ------------------------------------------------------------------
# Public Runtime State API
# ------------------------------------------------------------------
from camilladsp_autoswitch.infrastructure import runtime_state
from camilladsp_autoswitch.infrastructure.runtime_state import (
    CDSPState,
    load_state,
    save_state,
    update_state,
)

__all__ = [
    "runtime_state",
    "CDSPState",
    "load_state",
    "save_state",
    "update_state",
]
