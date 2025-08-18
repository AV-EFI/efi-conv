import json
from pathlib import Path
import pytest
from typing import Callable

@pytest.fixture(scope="module")
def input_path(request) -> Callable[[str], Path]:
    def get_path(filename):
        return request.path.parent / filename

    return get_path


@pytest.fixture(scope='module')
def expected_output(input_path):
    with input_path('efi_records.json').open() as f:
        return json.load(f)
