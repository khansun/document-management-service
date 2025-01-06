import click

from papermerge.core.features.auth.db.base import Base
from papermerge.core.features.auth.db.engine import engine
# loads user model into Base.metadata so that engine can create it
from papermerge.core.features.auth.models import User  # noqa


@click.command()
def cli():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    click.echo("Creating database...")
    cli()
