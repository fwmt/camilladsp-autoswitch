from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.domain.events import MediaActivityChanged, PolicyDecision
from camilladsp_autoswitch.application.handlers.media_policy_handler import MediaPolicyHandler
from camilladsp_autoswitch.domain.mapping import ProfileSelection


class FakeMapping:
    def select(self, media_active: bool):
        if media_active:
            return type(
                "Selection",
                (),
                {"profile": "cinema", "variant": "night"},
            )()
        return type(
            "Selection",
            (),
            {"profile": "music", "variant": None},
        )()

def test_media_active_publishes_cinema_decision():
    bus = EventBus()
    received = []

    bus.subscribe(PolicyDecision, lambda event: received.append(event))

    MediaPolicyHandler(bus, mapping=FakeMapping())

    bus.publish(MediaActivityChanged(active=True))

    assert len(received) == 1
    assert received[0].profile == "cinema"
    assert received[0].reason == "media_active"


def test_media_inactive_publishes_music_decision():
    bus = EventBus()
    received = []

    bus.subscribe(PolicyDecision, lambda event: received.append(event))

    MediaPolicyHandler(bus, mapping=FakeMapping())

    bus.publish(MediaActivityChanged(active=False))

    assert len(received) == 1
    assert received[0].profile == "music"
    assert received[0].reason == "media_inactive"
