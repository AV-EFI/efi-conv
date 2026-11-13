"""Command line wrapper around the AVefi records validator.

The rules live in :mod:`avefi_validate`, which is part of the
``avefi-schema`` distribution and therefore always matches the schema
it checks against. What stays here is what the conversion workflow
adds: the message naming the profile that has to be passed to the
converter, the limits taken from the environment, and the deprecated
``--update-schema`` option.

"""

import logging
import sys

from avefi_validate import (
    CheckResult,
    HashableId,
    Limits,
    check_file,
    exceeds_field_limit,
    get_schema_validator,
    has_invalid_value,
    placeholder_issuer_records,
    schema_fingerprint,
)
from avefi_validate import pass_checks as _pass_checks
import click

from .cli import cli_main, user_error
from .profiles import PLACEHOLDER_ISSUER_ID
from .settings import settings

log = logging.getLogger(__name__)

__all__ = [
    "CheckResult",
    "HashableId",
    "check",
    "exceeds_field_limit",
    "get_schema_validator",
    "has_invalid_value",
    "pass_checks",
    "placeholder_issuer_records",
    "schema_fingerprint",
]


def _limits() -> Limits:
    """Return the field length limits configured for this installation."""
    return Limits(
        line_limit=settings.line_limit, text_limit=settings.text_limit
    )


def pass_checks(
    efi_records,
    schema_validator,
    remove_invalid=False,
    preserve_status_removed=False,
    accept_placeholder_issuer=False,
):
    """Check records, applying the conversion workflow's conventions.

    See :func:`avefi_validate.pass_checks`.

    ``accept_placeholder_issuer`` is how the conversion spells "do not
    apply the placeholder issuer rule": the validator itself knows
    nothing about profiles and only applies the rule when it is told
    which issuer means "unspecified".

    """
    return _pass_checks(
        efi_records,
        schema_validator,
        remove_invalid=remove_invalid,
        preserve_status_removed=preserve_status_removed,
        placeholder_issuer_id=(
            None if accept_placeholder_issuer else PLACEHOLDER_ISSUER_ID
        ),
        limits=_limits(),
    )


def placeholder_issuer_message(efi_file, unnamed: list) -> str:
    """Return why a file naming no data provider is refused."""
    return (
        f"{efi_file}: {len(unnamed)} record(s) name the placeholder"
        f" issuer {PLACEHOLDER_ISSUER_ID}, so the data provider is"
        f" unspecified and no persistent identifier may be registered"
        f" for them. Convert again with --profile FILE naming the"
        f" institution, or pass --accept-placeholder-issuer to check"
        f" the records anyway while trying out a mapping."
    )


def _record(count: int) -> str:
    """Return ``record`` or ``records`` to match ``count``."""
    return "record" if count == 1 else "records"


@cli_main.command()
@click.option(
    "--preserve-status-removed",
    is_flag=True,
    default=False,
    help="Preserve items with access status Removed even without a PID yet.",
)
@click.option(
    "--remove-invalid/--no-remove-invalid",
    "-r",
    default=False,
    help="Remove invalid records modifying EFI_FILE in place.",
)
@click.option(
    "--update-schema",
    "-u",
    is_flag=True,
    default=False,
    help="Deprecated, does nothing: the schema ships with avefi-schema.",
)
@click.option(
    "--accept-placeholder-issuer",
    is_flag=True,
    default=False,
    help="Accept records that still name the documented placeholder"
    " issuer. For trying out a mapping only: records naming an"
    " unspecified data provider must not have identifiers registered.",
)
@click.argument(
    "efi_files", nargs=-1, type=click.Path(dir_okay=False, exists=True)
)
def check(
    efi_files,
    *,
    preserve_status_removed=False,
    remove_invalid=False,
    update_schema=False,
    accept_placeholder_issuer=False,
):
    """Sanity check EFI_FILES and optionally remove invalid records."""
    if update_schema:
        log.warning(
            "Ignoring --update-schema: the AVefi schema ships with the"
            " installed avefi-schema package. Upgrade that package to"
            " check against a newer schema."
        )
    schema_validator = get_schema_validator()
    for efi_file in efi_files:
        log.info(f"Processing {efi_file}")
        outcome = check_file(
            efi_file,
            schema_validator=schema_validator,
            remove_invalid=remove_invalid,
            preserve_status_removed=preserve_status_removed,
            placeholder_issuer_id=(
                None if accept_placeholder_issuer else PLACEHOLDER_ISSUER_ID
            ),
            limits=_limits(),
        )
        if outcome.unnamed:
            raise user_error(
                placeholder_issuer_message(efi_file, outcome.unnamed)
            )
        result = outcome.result
        if not result.passed:
            if remove_invalid:
                log.info(
                    f"Removed {result.invalid} invalid"
                    f" {_record(result.invalid)} and {result.dependants}"
                    f" dependant {_record(result.dependants)}"
                )
            else:
                log.error(
                    f"Found {result.invalid} invalid"
                    f" {_record(result.invalid)} ({result.dependants}"
                    f" dependant {_record(result.dependants)} would also"
                    f" be removed; no action taken)"
                )
                sys.exit(1)
        else:
            log.info(
                f"All {outcome.initial_count} records passed the checks"
                f" successfully"
            )
