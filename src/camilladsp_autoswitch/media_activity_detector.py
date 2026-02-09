# media_activity_detector.py

from camilladsp_autoswitch.events import (
    ProcessStarted,
    ProcessStopped,
    MediaActivityChanged,
)


class MediaActivityDetector:
    def __init__(self, bus, media_processes=None):
        self.bus = bus
        self.media_processes = set(media_processes or ["kodi"])
        self.active_processes = set()

        bus.subscribe(ProcessStarted, self.on_start)
        bus.subscribe(ProcessStopped, self.on_stop)

    def on_start(self, event):
        if event.name in self.media_processes:
            was_idle = not self.active_processes
            self.active_processes.add(event.name)

            if was_idle:
                self.bus.publish(MediaActivityChanged(active=True))

    def on_stop(self, event):
        if event.name in self.media_processes:
            self.active_processes.discard(event.name)

            if not self.active_processes:
                self.bus.publish(MediaActivityChanged(active=False))
