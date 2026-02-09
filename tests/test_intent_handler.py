from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.intent_handler import IntentHandler
from camilladsp_autoswitch.intent import SwitchIntent
from camilladsp_autoswitch.policy import PolicyDecision


def test_policy_decision_publishes_switch_intent():
    bus = EventBus()
    received = []

    bus.subscribe(SwitchIntent, lambda e: received.append(e))

    # register handler
    IntentHandler(bus)

    # publish input event
    bus.publish(
        PolicyDecision(
            profile="cinema",
            variant=None,
            reason="media_active",
        )
    )

    assert len(received) == 1
    assert isinstance(received[0], SwitchIntent)
    assert received[0].profile == "cinema"


def test_intent_handler_ignores_unrelated_events():
    bus = EventBus()
    received = []

    bus.subscribe(SwitchIntent, lambda e: received.append(e))
    IntentHandler(bus)

    class DummyEvent:
        pass

    bus.publish(DummyEvent())

    assert received == []
