from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.intent import SwitchIntent


class IntentExecutorHandler:
    """
    Executes SwitchIntent events.

    - resolves YAML
    - validates
    - applies
    - guarantees idempotency
    """

    def __init__(self, bus, resolve_yaml, validate, apply):
        self._resolve = resolve_yaml
        self._validate = validate
        self._apply = apply
        self._last_yaml = None

        bus.subscribe(SwitchIntent, self._on_intent)

    def _on_intent(self, intent: SwitchIntent) -> None:
        yaml = self._resolve(intent)

        if yaml == self._last_yaml:
            return

        result = self._validate(yaml)
        if not result.valid:
            return

        self._apply(yaml)
        self._last_yaml = yaml
