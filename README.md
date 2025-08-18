License: MIT
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# efi-conv

Reference repository for creating mappings to the [AVefi schema][]. If
you consider contributing data to the [AVefi project][], that is,
registering persistent identifiers for some audio-visual material in
your collection, this may be a good place to start. Contributions are
very welcome. Feel free to fork and submit pull requests or otherwise
get in touch and let us jointly work on your mapping.

[AVefi project]: https://projects.tib.eu/av-efi/
[AVefi schema]: https://av-efi.github.io/av-efi-schema/

## Usage example

For demonstration purposes and since this code is in early development
yet, just clone the repository and make an editable installation.
Either use pip in a virtualenv or preferably [UV][uv_install] if you consider
contributing and might need to add dependencies at some point.

Here is how to convert some test data:

```console
$ git clone https://github.com/AV-EFI/efi-conv.git
## [...]
$ cd efi-conv
$ pip install -e .
$ efi-conv --help
Usage: efi-conv [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.
  
Commands:
  check  Sanity check EFI_FILE and optionally remove invalid records.
  from   Convert files from some schema into a JSON file with AVefi records.
$ efi-conv from --help
Usage: efi-conv from [OPTIONS] OUTPUT_FILE [INPUT_FILES]...

  Convert files from some schema into a JSON file with AVefi records.

Options:
  -f, --format [avportal]  Source data format.
  --help                   Show this message and exit.
$ efi-conv from -f avportal efi_records.json tests/avportal/*.xml
$ efi-conv check tests/avportal/efi_records.json
INFO efi_conv.cli: All 6 records passed the checks successfully
## Or, instead of using pip above, proceed with UV:
$ uv sync
## [...]
$ uv run efi-conv --help
## Same output as above
$ uv run efi-conv from -f avportal efi_records.json tests/avportal/*.xml
$ uv run efi-conv check tests/avportal/efi_records.json
INFO efi_conv.cli: All 6 records passed the checks successfully
```

[uv_install]: https://docs.astral.sh/uv/getting-started/installation/

## Developer note

Add new converters as modules within the [efi_conv
package](./src/efi_conv). Then, add this module as another choice to
the format option in [cli.py](./src/efi_conv/cli.py) to make it
accessible from the command line. Take care that the module provides
`.module_name:efi_from` function similar to what the avportal module
does.

Unless you already have a suitable python parser for your data, check
out whether the [xsData][xsdata] or similar projects can help you
there. In fact, the [avportal module relies on xsData for
parsing](./src/efi_conv/avportal/README.md) as has been briefly
documented.

The actual mapping is the tedious part. See
[avportal.py](./src/efi_conv/avportal/avportal.py) for the kind of
work you are letting yourself in for. Also consult the [AVefi schema
documentation][AVefi schema].

[xsdata]: https://xsdata.readthedocs.io/
