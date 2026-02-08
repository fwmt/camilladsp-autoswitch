"""
Integration tests for process-based media detection inside autoswitch.
"""

from unittest.mock import patch

from camilladsp_autoswitch.autoswitch import detect_media_activity


@patch("camilladsp_autoswitch.autoswitch.is_process_running")
def test_media_active_when_kodi_running(mock_is_running):
    mock_is_running.return_value = True

    assert detect_media_activity() is True


@patch("camilladsp_autoswitch.autoswitch.is_process_running")
def test_media_inactive_when_no_process_running(mock_is_running):
    mock_is_running.return_value = False

    assert detect_media_activity() is False
"""
Integration tests for process-based media detection inside autoswitch.
"""

from unittest.mock import patch

from camilladsp_autoswitch.autoswitch import detect_media_activity


@patch("camilladsp_autoswitch.autoswitch.is_process_running")
def test_media_active_when_kodi_running(mock_is_running):
    mock_is_running.return_value = True

    assert detect_media_activity() is True


@patch("camilladsp_autoswitch.autoswitch.is_process_running")
def test_media_inactive_when_no_process_running(mock_is_running):
    mock_is_running.return_value = False

    assert detect_media_activity() is False
