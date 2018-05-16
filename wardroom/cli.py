import click

from wardroom.aws import aws


@click.group()
def cli():
    pass


cli.add_command(aws)
