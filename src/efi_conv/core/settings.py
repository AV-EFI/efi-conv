"""Settings that may be overridden through the environment."""

import os

# Derive the prefix from the top level package rather than this
# module's package: __package__ is "efi_conv.core" here, and
# environment variable names cannot contain a dot.
ENV_PREFIX = f"{__package__.split('.')[0].upper()}_"


class Settings:
    """Limits used by the converters and by the check command.

    ``EFI_CONV_LINE_LIMIT`` and ``EFI_CONV_TEXT_LIMIT`` override the
    defaults. The wording of the variables is part of the interface:
    they existed before this module stopped using ``pydantic-settings``
    to read them.

    """

    def __init__(self):
        self.line_limit = int(os.environ.get(f"{ENV_PREFIX}LINE_LIMIT", "250"))
        self.text_limit = int(
            os.environ.get(f"{ENV_PREFIX}TEXT_LIMIT", "8192")
        )


settings = Settings()
