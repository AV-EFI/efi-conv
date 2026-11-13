"""Reading and writing AVefi records.

The implementation lives in :mod:`avefi_validate.io`, so that the
converters and the validator share one definition of the record format
and of the atomic write. This module keeps the name the rest of
``efi-conv`` imports.

"""

from avefi_validate.io import (
    CATEGORY_ORDER,
    ENCODING,
    dump,
    dumps,
    load,
    loads,
    sort_records,
)

__all__ = [
    "CATEGORY_ORDER",
    "ENCODING",
    "dump",
    "dumps",
    "load",
    "loads",
    "sort_records",
]
