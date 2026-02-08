"""
Tests for the process-based activity detector.

These tests verify that the detector correctly determines
whether a given process is running, without depending on
the actual system process table.
"""

import subprocess
from unittest.mock import patch

from camilladsp_autoswitch.detectors.process import is_process_running


@patch("subprocess.check_output")
def test_process_running(mock_check_output):
    """
    If pgrep returns any output, the process is considered running.
    """
    mock_check_output.return_value = b"1234\n"

    assert is_process_running("kodi") is True


@patch("subprocess.check_output")
def test_process_not_running(mock_check_output):
    """
    If pgrep raises CalledProcessError, the process is not running.
    """
    mock_check_output.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["pgrep", "-x", "kodi"],
    )

    assert is_process_running("kodi") is False


@patch("subprocess.check_output")
def test_exact_process_name_is_used(mock_check_output):
    """
    Ensure the detector uses exact process matching (-x).
    """
    mock_check_output.return_value = b"999\n"

    is_process_running("kodi")

    mock_check_output.assert_called_with(
        ["pgrep", "-x", "kodi"],
        stderr=subprocess.DEVNULL,
    )
