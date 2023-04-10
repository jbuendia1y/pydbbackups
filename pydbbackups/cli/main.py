import click
import getpass

from rich.table import Table
from rich.console import Console
from pydbbackups.cli.config import build_config
from pydbbackups.cli.services import BackupsService


@click.group()
def app():
    """ Awesome APP """


@app.command(name='list')
def get_backups():
    table = Table()

    table.add_column('Nombre')
    table.add_column('Base de datos')
    table.add_column('Fecha')

    for bfile, bdata in BackupsService.list_backups():
        table.add_row(bfile.name, bdata.database_name, bfile.date)

    console = Console()
    console.print(table)


@app.command(name='run')
@click.option('--name', required=True)
@click.option('--database-type', required=True, type=click.Choice(['postgres', 'mongodb']))
@click.option('--host', required=True)
@click.option('--database', required=True)
@click.option('--username', default=None)
@click.option('--password', default=None)
@click.option('--without-password', default=False)
@click.option('--port', default=None)
@click.option('--compress', default=None)
def make_backup(name: str, database_type, host, database, username, password, without_password, port, compress):
    name = name.replace('-', '_')

    if without_password is False and password is None:
        password = getpass.getpass('Password: ')

    if without_password is True:
        password = None

    service = BackupsService.build(
        database_type,
        name=name,
        host=host,
        database=database,
        username=username,
        password=password,
        port=port,
        compress=compress)

    service.dump(name)


def main():
    build_config()
    app()


if __name__ == '__main__':
    main()
