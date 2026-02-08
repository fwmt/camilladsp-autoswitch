from pathlib import Path
import textwrap

import pytest

from camilladsp_autoswitch.validator import validate, ValidationResult


def test_missing_yaml_is_invalid(tmp_path):
    missing = tmp_path / "missing.yml"

    result = validate(missing)

    assert result.valid is False
    assert "not found" in result.reason.lower()


def test_invalid_yaml_syntax(tmp_path):
    bad = tmp_path / "bad.yml"
    bad.write_text("this: [ is: not: valid")

    result = validate(bad)

    assert result.valid is False
    assert "syntax" in result.reason.lower() or "parse" in result.reason.lower()


def test_valid_yaml_passes(tmp_path):
    good = tmp_path / "good.yml"
    good.write_text(
        textwrap.dedent(
            """
            devices:
              samplerate: 48000
              chunksize: 1024
            """
        )
    )

    result = validate(good)

    assert result.valid is True
    assert result.reason is None


def test_validator_never_raises(tmp_path):
    weird = tmp_path / "weird.yml"
    weird.write_text("!!!")

    # Must never raise
    result = validate(weird)

    assert isinstance(result, ValidationResult)
