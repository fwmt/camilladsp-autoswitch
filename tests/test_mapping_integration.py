from pathlib import Path
from unittest.mock import MagicMock

from camilladsp_autoswitch.bootstrap import bootstrap
from camilladsp_autoswitch.events import ProcessStarted, ProcessStopped
from camilladsp_autoswitch.mapping.media import MediaMapping
from camilladsp_autoswitch.mapping.media import ProfileSelection


def test_mapping_yaml_drives_runtime_behavior(tmp_path):
    """
    Integration test:
    mapping.yml is the SINGLE source of truth.
    """

    # ---------------------------------------
    # Arrange: fake mapping (equivalent to YAML)
    # ---------------------------------------

    mapping = MediaMapping(
        on=ProfileSelection(
            profile="cinema",
            variant="night",
        ),
        off=ProfileSelection(
            profile="music",
            variant="normal",
        ),
    )

    apply = MagicMock()
    validate = MagicMock()
    validate.return_value.valid = True
    validate.return_value.reason = None

    resolve_yaml = MagicMock(
        side_effect=lambda decision, **_: (
            f"/fake/{decision.profile}.{decision.variant or 'default'}.yml"
        )
    )

    bus = bootstrap(
        mapping=mapping,
        resolve_yaml=resolve_yaml,
        validate_fn=validate,
        apply_fn=apply,
    )

    # ---------------------------------------
    # Act: media ON
    # ---------------------------------------

    bus.publish(ProcessStarted(name="kodi"))

    # ---------------------------------------
    # Assert: cinema.night applied
    # ---------------------------------------

    apply.assert_called_with("/fake/cinema.night.yml")

    apply.reset_mock()

    # ---------------------------------------
    # Act: media OFF
    # ---------------------------------------

    bus.publish(ProcessStopped(name="kodi"))

    # ---------------------------------------
    # Assert: music.normal applied
    # ---------------------------------------

    apply.assert_called_with("/fake/music.normal.yml")
