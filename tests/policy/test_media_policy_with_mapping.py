from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.domain.events import MediaActivityChanged
from camilladsp_autoswitch.domain.events import PolicyDecision
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

def test_policy_emits_decision_when_media_on():
    bus = EventBus()
    mapping = FakeMapping()

    MediaPolicyHandler(bus, mapping=mapping)

    decisions = []
    bus.subscribe(PolicyDecision, lambda e: decisions.append(e))

    bus.publish(MediaActivityChanged(active=True))

    assert len(decisions) == 1
    assert decisions[0].profile == "cinema"
    assert decisions[0].variant == "night"
    assert decisions[0].reason == "media_active"


def test_policy_emits_decision_when_media_off():
    bus = EventBus()
    mapping = FakeMapping()

    MediaPolicyHandler(bus, mapping=mapping)

    decisions = []
    bus.subscribe(PolicyDecision, lambda e: decisions.append(e))

    bus.publish(MediaActivityChanged(active=False))

    assert len(decisions) == 1
    assert decisions[0].profile == "music"
    assert decisions[0].variant is None
    assert decisions[0].reason == "media_inactive"
