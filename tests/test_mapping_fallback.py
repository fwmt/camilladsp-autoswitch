from camilladsp_autoswitch.mapping.loader import load_media_mapping
from camilladsp_autoswitch.mapping.media import MediaMapping


def test_fallback_mapping_when_file_missing(tmp_path):
    mapping = load_media_mapping(
        path=tmp_path / "does-not-exist.yml",
        allow_fallback=True,
    )

    assert isinstance(mapping, MediaMapping)
    assert mapping.on.profile == "cinema"
    assert mapping.off.profile == "music"
