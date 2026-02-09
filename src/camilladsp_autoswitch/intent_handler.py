from camilladsp_autoswitch.policy import PolicyDecision
from camilladsp_autoswitch.intent import SwitchIntent


class IntentHandler:
    def __init__(self, bus):
        self._bus = bus
        original_publish = bus.publish

        def publish(event):
            # 🎯 reage SOMENTE ao evento esperado
            if isinstance(event, PolicyDecision):
                intent = SwitchIntent(
                    profile=event.profile,
                    variant=event.variant,
                    reason=event.reason,
                )
                original_publish(intent)
                return  # ⛔ consome o evento

            # ❌ ignora completamente eventos irrelevantes
            return

        bus.publish = publish
