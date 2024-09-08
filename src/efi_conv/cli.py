import importlib
import logging
import logging.config
import os
import sys

import click

from . import avefi


log = logging.getLogger(__name__)
loglevel = os.environ.get(
    f"{__package__.upper()}_LOGLEVEL", 'INFO').upper()
logging_config = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': loglevel,
            'formatter': 'simple',
            'stream': 'ext://sys.stderr',
        },
    },
    'loggers': {
        __package__: {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
    'disable_existing_loggers': False,
}
logging.config.dictConfig(logging_config)


@click.group()
def cli_main():
    pass


@cli_main.command('from')
@click.option(
    '-f', '--format', type=click.Choice(['avportal']),
    help='Source data format.')
@click.argument('output_file', type=click.Path(dir_okay=False, writable=True))
@click.argument('input_files', nargs=-1, type=click.Path(exists=True))
def efi_from(output_file, input_files, **kwargs):
    """Convert files from some schema into a JSON file with AVefi records."""
    mod = importlib.import_module(f".{kwargs['format']}", __package__)
    generated_records = []
    for input_file in input_files:
        try:
            result = mod.efi_import(input_file)
        except Exception as e:
            raise RuntimeError(f"Failed to convert {input_file}") from e
        for record in result:
            if not(record.has_identifier):
                raise ValueError(
                    f"has_identifier missing for some record in {input_file}")
            if not(record.has_source_key):
                log.warning(
                    f"Records with unspecified source key in {input_file},"
                    f" copying identifier to fill the gap")
                record.has_source_key.append(record.has_identifier[0].id)
        generated_records.extend(result)
    if generated_records:
        avefi.dump(generated_records, output_file)


@cli_main.command()
@click.option(
    '--remove-invalid/--no-remove-invalid', '-r', default=False,
    help='Remove invalid records modifying EFI_FILE in place.')
@click.argument('efi_file', type=click.Path(dir_okay=False, exists=True))
def check(efi_file, *, remove_invalid=False):
    """Sanity check EFI_FILE and optionally remove invalid records."""
    from . import check

    efi_records = avefi.load(efi_file)
    old_count = len(efi_records)
    if not check.pass_checks(efi_records, remove_invalid=True):
        if remove_invalid:
            avefi.dump(efi_records, efi_file)
            log.info(
                f"Successfully removed {old_count-len(efi_records)} invalid"
                f" records")
        else:
            log.error(
                f"Found {old_count-len(efi_records)} invalid records"
                f" (no action taken)")
            sys.exit(1)
    else:
        log.info(f"All {old_count} records passed the checks successfully")
