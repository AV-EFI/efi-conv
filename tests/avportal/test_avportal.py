import json

import pytest

from efi_conv.core import avefi, check
from efi_conv.avportal import avportal

@pytest.fixture(scope='module')
def parsed_input(input_path):
    return avportal.read_input(input_path('clip27540.xml'))


def test_map_to_efi(parsed_input, expected_output):
    efi_records = avportal.map_to_efi(parsed_input)
    result_serialized = json.loads(avefi.dumps(efi_records))

    assert result_serialized == expected_output


def test_schema_compliance(parsed_input):
    schema_validator = check.get_schema_validator()
    efi_records = avportal.map_to_efi(parsed_input)
    assert check.pass_checks(efi_records, schema_validator), \
        "Mapped data did not validate"
