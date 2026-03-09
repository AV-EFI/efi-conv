# To be imported in each subcommand module

import click

IMPORTERS = ["avportal", "fmdu"]


@click.group()
def cli_main():
    pass
