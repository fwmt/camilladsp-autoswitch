from camilladsp_autoswitch.intent import SwitchIntent
from camilladsp_autoswitch.policy import PolicyDecision


class IntentHandler:
    """
    Translates PolicyDecision → SwitchIntent
    """

    def __init__(self, bus):
        self._bus = bus
        bus.subscribe(PolicyDecision, self._on_policy_decision)

    def _on_policy_decision(self, event: PolicyDecision):
        intent = SwitchIntent(
            profile=event.profile,
            variant=event.variant,
            reason=event.reason,
        )
        self._bus.publish(intent)
