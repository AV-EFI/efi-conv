import importlib

import click

from . import avefi


@click.command()
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
