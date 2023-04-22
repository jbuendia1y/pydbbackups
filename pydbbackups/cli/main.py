import getpass
import time
import click
import inquirer

from rich.table import Table
from rich.console import Console
from pydbbackups.cli.config import build_config
from pydbbackups.cli.services import BackupsService

AVAILABLE_DUMP_DB = ['postgres', 'mongodb', 'mysql']
AVAILABLE_RESTORE_DB = ['postgres', 'mongodb', 'mysql']


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option('0.1.0', prog_name='dbbackups')
def app():
    """ Awesome APP """


@app.command(name='list')
def get_backups():
    table = Table()

    table.add_column('ID')
    table.add_column('Nombre')
    table.add_column('Base de datos')
    table.add_column('Fecha')

    for _, bdata in BackupsService.list_backups():
        table.add_row(
            f"{bdata.id}",
            f"{bdata.name}.{bdata.ext}",
            bdata.database_name,
            bdata.created_at.strftime('%d/%m/%y %H:%M:%S')
        )

    console = Console()
    console.print(table)


@app.command(name='dump')
@click.option('--name', required=True)
@click.option('--database-type', required=True, type=click.Choice(AVAILABLE_DUMP_DB))
@click.option('--host', required=True)
@click.option('--database', required=True)
@click.option('--username', default=None)
@click.option('--password', default=None)
@click.option('--without-password', default=False)
@click.option('--port', default=None)
@click.option('--compress', default=None, is_flag=True)
@click.option('--format', default=None)
@click.option('--file', required=False, default=None)
def make_backup(**kwargs):
    name = kwargs.get('name').replace('-', '_')
    without_password = kwargs.get('without_password')
    database_type = kwargs.get('without_password')
    compress = kwargs.get('compress')

    if without_password is False and password is None:
        password = getpass.getpass('Password: ')

    if without_password is True:
        password = None

    service = BackupsService.build(
        database_type,
        host=kwargs.get('host'),
        database=kwargs.get('database'),
        username=kwargs.get('username'),
        password=kwargs.get('password'),
        port=kwargs.get('port'),
    )

    console = Console()
    with console.status("[bold green]Dumping database ..."):
        service.dump(name, compress=compress, **kwargs)
        time.sleep(1)
    console.print("[bold green] Backup created !")


@app.command(name='restore')
@click.option('--database-type', required=True, type=click.Choice(AVAILABLE_RESTORE_DB))
@click.option('--host', required=True)
@click.option('--port', default=None)
@click.option('--database', required=True)
@click.option('--username', required=True)
@click.option('--password', default=None)
@click.option('--without-password', default=False)
def restore_backup(**kwargs):
    without_password = kwargs.get('without_password')
    database_type = kwargs.get('database_type')

    if without_password is False and password is None:
        password = getpass.getpass('Password: ')

    if without_password is True:
        password = None

    service = BackupsService.build(
        database_type,
        host=kwargs.get('host'),
        port=kwargs.get('port'),
        database=kwargs.get('database'),
        username=kwargs.get('username'),
        password=password
    )
    console = Console()

    backups = list(BackupsService.list_backups())
    backups.sort(key=lambda v: v[1].id)
    backups = [
        f"{d.id} - {d.name}.{d.ext} - {d.database_name}" for _, d in backups]

    questions = [
        inquirer.List(
            name='backup',
            message='Select the backup to restore',
            choices=backups
        )
    ]
    answers = inquirer.prompt(questions)

    if not answers:
        raise ValueError('We need than you selected a backup to restore')

    backup_id = int(answers['backup'].split(' - ')[0])
    finded_backup = BackupsService.get_backup(backup_id)

    with console.status("[bold green]Restoring backup ..."):
        service.restore(finded_backup.backup)
        time.sleep(1)
    console.print("[bold green]Backup restored !")


def main():
    build_config()
    app()


if __name__ == '__main__':
    main()
