from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.policy import PolicyDecision
from camilladsp_autoswitch.intent import SwitchIntent
from camilladsp_autoswitch.intent_handler import IntentHandler


def test_policy_decision_publishes_switch_intent():
    bus = EventBus()
    published = []

    # intercepta publicações do bus
    bus.publish = lambda event: published.append(event)

    # registra o handler
    IntentHandler(bus)

    # dispara o evento de entrada
    bus.publish(
        PolicyDecision(
            profile="cinema",
            variant=None,
            reason="media_active",
        )
    )

    assert len(published) == 1
    assert isinstance(published[0], SwitchIntent)
    assert published[0].profile == "cinema"
    assert published[0].variant is None
    assert published[0].reason == "media_active"

def test_policy_decision_with_variant_is_preserved():
    bus = EventBus()
    published = []

    bus.publish = lambda event: published.append(event)
    IntentHandler(bus)

    bus.publish(
        PolicyDecision(
            profile="music",
            variant="night",
            reason="manual_mode",
        )
    )

    intent = published[0]

    assert intent.profile == "music"
    assert intent.variant == "night"
    assert intent.reason == "manual_mode"

def test_intent_handler_ignores_unrelated_events():
    bus = EventBus()
    published = []

    bus.publish = lambda event: published.append(event)
    IntentHandler(bus)

    class DummyEvent:
        pass

    bus.publish(DummyEvent())

    assert published == []
