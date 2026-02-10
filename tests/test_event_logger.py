import logging

from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.infrastructure.eventing.event_logger import EventLogger
from camilladsp_autoswitch.domain.events import Event


class DummyEvent(Event):
    def __init__(self, value: str):
        self.value = value

    def __repr__(self) -> str:
        return f"value={self.value}"


def test_event_logger_logs_published_events(caplog):
    bus = EventBus()
    EventLogger(bus)

    event = DummyEvent("test")

    with caplog.at_level(logging.INFO, logger="camilladsp_autoswitch.domain.events"):
        bus.publish(event)

    assert len(caplog.records) == 1

    record = caplog.records[0]

    assert "EVENT: DummyEvent" in record.message
    assert "value=test" in record.message
