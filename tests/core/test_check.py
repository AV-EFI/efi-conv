"""The check command, as a user sees it.

The rules themselves are tested in av-efi-schema. What is tested here
is the contract of this command: what it reports, when it rewrites a
file, and the placeholder issuer rule, which exists because the
converters have to name a data provider they do not know.

"""

import copy
import json
import logging

from click.testing import CliRunner

from efi_conv.core import profiles
from efi_conv.main import cli_main

WORK = {
    "category": "avefi:WorkVariant",
    "type": "Monographic",
    "has_primary_title": {
        "type": "PreferredTitle",
        "has_name": "Die Brücke",
    },
    "has_identifier": [{"category": "avefi:LocalResource", "id": "w1"}],
}
MANIFESTATION = {
    "category": "avefi:Manifestation",
    "has_primary_title": {"type": "TitleProper", "has_name": "Die Brücke"},
    "is_manifestation_of": [{"category": "avefi:LocalResource", "id": "w1"}],
    "has_identifier": [{"category": "avefi:LocalResource", "id": "m1"}],
}
ITEM = {
    "category": "avefi:Item",
    "has_primary_title": {"type": "TitleProper", "has_name": "Die Brücke"},
    "is_item_of": {"category": "avefi:LocalResource", "id": "m1"},
    "has_identifier": [{"category": "avefi:LocalResource", "id": "i1"}],
}


def _write(tmp_path, *record_dicts, name="records.json"):
    target = tmp_path / name
    target.write_text(json.dumps(list(record_dicts)), encoding="utf-8")
    return target


def _overlong_work():
    work = copy.deepcopy(WORK)
    work["has_primary_title"]["has_name"] = "x" * 1000
    return work


def _broken(tmp_path):
    """Return a file whose work violates the title length limit."""
    return _write(tmp_path, _overlong_work(), MANIFESTATION, ITEM)


def _placeholder(tmp_path):
    work = copy.deepcopy(WORK)
    work["described_by"] = [
        {
            "has_issuer_id": profiles.PLACEHOLDER_ISSUER_ID,
            "has_issuer_name": "Unspecified data provider",
            "has_source_key": ["k1"],
        }
    ]
    return _write(tmp_path, work, MANIFESTATION, ITEM)


class TestReportsCounts:
    """The command reports invalid and dependant records apart."""

    def test_no_action_reports_both_counts(self, tmp_path, caplog):
        caplog.set_level(logging.INFO)
        target = _broken(tmp_path)
        result = CliRunner().invoke(cli_main, ["check", str(target)])
        assert result.exit_code != 0
        assert "1 invalid record" in caplog.text
        assert "2 dependant records" in caplog.text

    def test_no_action_does_not_rewrite_the_file(self, tmp_path, caplog):
        caplog.set_level(logging.INFO)
        target = _broken(tmp_path)
        before = target.read_text(encoding="utf-8")
        CliRunner().invoke(cli_main, ["check", str(target)])
        assert target.read_text(encoding="utf-8") == before

    def test_remove_invalid_reports_both_counts(self, tmp_path, caplog):
        caplog.set_level(logging.INFO)
        target = _broken(tmp_path)
        result = CliRunner().invoke(
            cli_main, ["check", "--remove-invalid", str(target)]
        )
        assert result.exit_code == 0
        assert "1 invalid record" in caplog.text
        assert "2 dependant records" in caplog.text
        assert json.loads(target.read_text(encoding="utf-8")) == []

    def test_a_valid_file_passes(self, tmp_path, caplog):
        caplog.set_level(logging.INFO)
        target = _write(tmp_path, WORK, MANIFESTATION, ITEM)
        result = CliRunner().invoke(cli_main, ["check", str(target)])
        assert result.exit_code == 0, result.output
        assert "All 3 records passed" in caplog.text


class TestPlaceholderIssuer:
    """A file naming no data provider must not reach registration.

    ``efi-conv from`` refuses to convert with the placeholder issuer
    unless it is told to, but a file produced that way, or produced by
    running a converter as ``python -m efi_conv.NAME``, still reaches
    ``check``. The documented pipeline is from, check, register
    identifiers, so ``check`` is the last step that can notice it.

    """

    def test_the_command_exits_non_zero(self, tmp_path):
        target = _placeholder(tmp_path)
        result = CliRunner().invoke(cli_main, ["check", str(target)])
        assert result.exit_code != 0
        assert "placeholder" in result.output.lower()

    def test_the_flag_accepts_it(self, tmp_path):
        target = _placeholder(tmp_path)
        result = CliRunner().invoke(
            cli_main,
            ["check", "--accept-placeholder-issuer", str(target)],
        )
        assert result.exit_code == 0, result.output

    def test_removing_invalid_records_does_not_hide_it(self, tmp_path):
        """--remove-invalid must not answer this by emptying the file."""
        target = _placeholder(tmp_path)
        before = target.read_text(encoding="utf-8")
        result = CliRunner().invoke(
            cli_main, ["check", "--remove-invalid", str(target)]
        )
        assert result.exit_code != 0
        assert target.read_text(encoding="utf-8") == before


class TestUpdateSchema:
    """The option is kept so that existing invocations keep working."""

    def test_it_warns_and_still_checks(self, tmp_path, caplog):
        caplog.set_level(logging.INFO)
        target = _write(tmp_path, WORK, MANIFESTATION, ITEM)
        result = CliRunner().invoke(
            cli_main, ["check", "--update-schema", str(target)]
        )
        assert result.exit_code == 0, result.output
        assert "--update-schema" in caplog.text
        assert "All 3 records passed" in caplog.text
