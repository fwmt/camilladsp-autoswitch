"""
Media activity source via DBus (MPRIS compatible).
"""

from camilladsp_autoswitch.events import MediaActivityChanged


class DbusMediaActivitySource:
    def __init__(self, bus, dbus_client):
        self._bus = bus
        self._dbus = dbus_client

    def start(self) -> None:
        self._dbus.on_playing(self._on_playing)
        self._dbus.on_stopped(self._on_stopped)

    def _on_playing(self):
        self._bus.publish(MediaActivityChanged(active=True))

    def _on_stopped(self):
        self._bus.publish(MediaActivityChanged(active=False))
