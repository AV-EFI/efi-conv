from linkml_runtime.utils.formatutils import remove_empty_items
import pytest

from efi_conv import check
from efi_conv.avportal import avportal

@pytest.fixture(scope='module')
def parsed_input(input_path):
    return avportal.read_input(input_path('clip27540.xml'))


def test_map_to_efi(parsed_input, expected_output):
    efi_records = avportal.map_to_efi(parsed_input)
    result_serialized = remove_empty_items(efi_records)

    assert result_serialized == expected_output


def test_schema_compliance(parsed_input):
    schema_validator = check.get_schema_validator()
    efi_records = avportal.map_to_efi(parsed_input)
    assert check.pass_checks(efi_records, schema_validator), \
        "Mapped data did not validate"
