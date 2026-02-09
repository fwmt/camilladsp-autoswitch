from camilladsp_autoswitch.intent import (
    SwitchIntent,
    build_intent_from_policy,
)
from camilladsp_autoswitch.policy import PolicyDecision


def test_media_active_creates_switch_intent():
    decision = PolicyDecision(
        profile="cinema",
        variant=None,
        reason="media_active",
    )

    intent = build_intent_from_policy(decision)

    assert isinstance(intent, SwitchIntent)
    assert intent.profile == "cinema"
    assert intent.variant is None
    assert intent.reason == "media_active"


def test_media_inactive_creates_switch_intent():
    decision = PolicyDecision(
        profile="music",
        variant=None,
        reason="media_inactive",
    )

    intent = build_intent_from_policy(decision)

    assert intent.profile == "music"
    assert intent.reason == "media_inactive"


def test_manual_mode_creates_switch_intent():
    decision = PolicyDecision(
        profile="custom",
        variant="night",
        reason="manual_mode",
    )

    intent = build_intent_from_policy(decision)

    assert intent.profile == "custom"
    assert intent.variant == "night"
    assert intent.reason == "manual_mode"
