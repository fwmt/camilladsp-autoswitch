from unittest.mock import MagicMock
from camilladsp_autoswitch.event_bus import EventBus
from camilladsp_autoswitch.bootstrap import bootstrap
from camilladsp_autoswitch.domain.events import ProcessStarted

def test_full_event_pipeline_triggers_apply():
    apply = MagicMock()
    validate = MagicMock()
    validate.return_value.valid = True
    validate.return_value.reason = None

    resolve = MagicMock(return_value="/tmp/cinema.yml")

    bus = bootstrap(
        resolve_yaml=resolve,
        validate_fn=validate,
        apply_fn=apply,
    )

    # 🔥 evento externo
    bus.publish(ProcessStarted(name="kodi"))

    apply.assert_called_once_with("/tmp/cinema.yml")
