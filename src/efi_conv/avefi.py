from avefi_schema import model as efi
from linkml_runtime import dumpers, loaders


def load(source):
    """Load AVefi records from file or string."""
    return loaders.json_loader.load_any(source, efi.MovingImageRecord)


def dump(records, to_file, **kwargs):
    """Dump AVefi records to JSON file."""
    if 'inject_type' not in kwargs:
        kwargs['inject_type'] = False
    dumpers.json_dumper.dump(records, to_file, **kwargs)


def dumps(records):
    """Dump AVefi records to string (in JSON format)."""
    return dumpers.json_dumper.dumps(records, inject_type=False)
