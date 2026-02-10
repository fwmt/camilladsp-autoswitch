from camilladsp_autoswitch.infrastructure.detectors.process import is_process_running

MEDIA_PROCESS_NAMES = ["kodi"]

def detect_media_activity() -> bool:
    return any(is_process_running(name) for name in MEDIA_PROCESS_NAMES)
