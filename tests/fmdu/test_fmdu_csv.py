import json

from efi_conv.core import avefi, check, from_
from efi_conv.fmdu import csv as fmdu_csv


def test_map_to_efi(input_path, expected_output):
    efi_records = from_.import_file(fmdu_csv, input_path("sample_data.csv"))
    result_serialized = json.loads(avefi.dumps(efi_records))

    assert result_serialized == expected_output


def test_schema_compliance(input_path):
    schema_validator = check.get_schema_validator()
    efi_records = from_.import_file(fmdu_csv, input_path("sample_data.csv"))
    assert check.pass_checks(efi_records, schema_validator), (
        "Mapped data did not validate"
    )
