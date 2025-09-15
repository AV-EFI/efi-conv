import json

import pytest

from efi_conv.core import avefi, check, from_
from efi_conv.avportal import avportal

def test_map_to_efi(input_path, expected_output):
    efi_records = from_.import_file(avportal, input_path('clip27540.xml'))
    result_serialized = json.loads(avefi.dumps(efi_records))

    assert result_serialized == expected_output


def test_schema_compliance(input_path):
    schema_validator = check.get_schema_validator()
    efi_records = from_.import_file(avportal, input_path('clip27540.xml'))
    assert check.pass_checks(efi_records, schema_validator), \
        "Mapped data did not validate"
