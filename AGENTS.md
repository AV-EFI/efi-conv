# OpenCode Agent Instructions

## Setup
- Install dependencies: `uv sync --no-python-downloads`
- Run the CLI: `uv run efi-conv --help`

## Development
- Install pre-commit hooks: `pipx install pre-commit && pre-commit install`
- Add new converters as modules in `src/efi_conv` and register them in `IMPORTERS` in `src/efi_conv/core/cli.py`

## Testing
- Run tests: `uv run coverage run -m pytest`
- Generate coverage report: `uv run coverage report -m`

## Quality Checks
- Lint: `uv run ruff check --output-format=github`
- Format: `uv run ruff format --diff`

## Project Structure
- `src/efi_conv`: Main package
- `tests`: Test files
- `src/efi_conv/avportal`: AVPortal converter module
- `src/efi_conv/fmdu`: FMDU converter module

## Key Files
- `pyproject.toml`: Project configuration
- `.github/workflows/main.yml`: CI workflow
- `.pre-commit-config.yaml`: Pre-commit hooks

## Converter Requirements
- Each converter module must provide a `.module_name:efi_import` function
- Register new converters in `IMPORTERS` list in `src/efi_conv/core/cli.py`
