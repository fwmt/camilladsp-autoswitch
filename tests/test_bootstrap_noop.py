from unittest.mock import MagicMock
from camilladsp_autoswitch.bootstrap import bootstrap
from camilladsp_autoswitch.events import ProcessStarted

def test_bootstrap_does_not_apply_when_validation_fails():
    apply = MagicMock()
    validate = MagicMock()
    validate.return_value.valid = False
    validate.return_value.reason = "invalid"

    resolve_yaml = MagicMock(return_value="/tmp/broken.yml")

    bus = bootstrap(
        resolve_yaml=resolve_yaml,
        validate_fn=validate,
        apply_fn=apply,
    )

    bus.publish(ProcessStarted(name="kodi"))

    apply.assert_not_called()
