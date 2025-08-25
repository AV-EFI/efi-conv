import pathlib
from typing import Annotated

from avefi_schema import model_pydantic_v2 as efi

def load(source: str) -> list[efi.MovingImageRecord]:
    """Load AVefi records from file or string."""
    with pathlib.Path(source).open() as f:
        container = efi.MovingImageRecords.model_validate_json(f.read())
    return container.root


def dump(records: list[efi.MovingImageRecord], to_file: str):
    """Dump AVefi records to JSON file."""
    with open(to_file, 'w') as f:
        f.write(dumps(records, indent=2))


def dumps(records: list[efi.MovingImageRecord], indent=None) -> str:
    """Dump AVefi records to string (in JSON format)."""
    container = efi.MovingImageRecords(records)
    return container.model_dump_json(exclude_none=True, indent=indent)
