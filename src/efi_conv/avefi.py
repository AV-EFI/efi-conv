from typing import List

from avefi_schema import model as efi
from linkml_runtime import dumpers, loaders


def load(source: str) -> List[efi.MovingImageRecord]:
    """Load AVefi records from file or string."""
    result = loaders.json_loader.load_any(source, efi.MovingImageRecord)
    if not isinstance(result, list):
        result = [result]
    return result


def dump(records: List[efi.MovingImageRecord], to_file: str, **kwargs):
    """Dump AVefi records to JSON file."""
    if 'inject_type' not in kwargs:
        kwargs['inject_type'] = False
    dumpers.json_dumper.dump(records, to_file, **kwargs)


def dumps(records: List[efi.MovingImageRecord]) -> str:
    """Dump AVefi records to string (in JSON format)."""
    return dumpers.json_dumper.dumps(records, inject_type=False)
