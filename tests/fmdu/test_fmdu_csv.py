from linkml_runtime.utils.formatutils import remove_empty_items
import pytest

from efi_conv import check
from efi_conv.fmdu import csv as fmdu_csv

@pytest.fixture(scope='module')
def parsed_input(input_path):
    return fmdu_csv.read_input(input_path('sample_data.csv'))


def test_map_to_efi(parsed_input, expected_output):
    efi_records = fmdu_csv.map_to_efi(parsed_input)
    result_serialized = remove_empty_items(efi_records)

    assert result_serialized == expected_output


def test_schema_compliance(parsed_input):
    schema_validator = check.get_schema_validator()
    efi_records = fmdu_csv.map_to_efi(parsed_input)
    assert check.pass_checks(efi_records, schema_validator), \
        "Mapped data did not validate"
