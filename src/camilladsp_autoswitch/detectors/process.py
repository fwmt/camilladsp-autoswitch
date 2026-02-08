"""
Process-based activity detector.

This module provides a simple and generic mechanism to detect
whether a given process is currently running on the system.

It is intentionally application-agnostic and can be reused
to detect any process (e.g. kodi, mpv, plex, spotifyd).

Design principles:
- No direct dependency on CamillaDSP
- No side effects
- Fail-safe: never raise errors to callers
- Easy to unit test (subprocess is mockable)
"""

import subprocess


def is_process_running(name: str) -> bool:
    """
    Check whether a process with the given name is running.

    This uses `pgrep -x` to ensure an exact match on the process name,
    avoiding false positives (e.g. 'kodi' vs 'kodi-helper').

    Args:
        name: Exact process name to search for (e.g. 'kodi').

    Returns:
        True if at least one matching process is running.
        False if no process is found or if an error occurs.
    """
    try:
        output = subprocess.check_output(
            ["pgrep", "-x", name],
            stderr=subprocess.DEVNULL,
        )

        # Any non-empty output means at least one PID matched
        return bool(output.strip())

    except subprocess.CalledProcessError:
        # pgrep returns exit code 1 when no process is found
        return False

    except Exception:
        # Absolute safety net: never let unexpected errors
        # propagate and affect the autoswitch daemon
        return False
