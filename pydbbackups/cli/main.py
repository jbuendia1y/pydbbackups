import click
import getpass
import inquirer
import time

from rich.table import Table
from rich.console import Console
from pydbbackups.cli.config import build_config
from pydbbackups.cli.services import BackupsService


@click.group(invoke_without_command=True, no_args_is_help=True)
@click.version_option('0.0.4', prog_name='dbbackups')
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
@click.option('--database-type', required=True, type=click.Choice(['postgres', 'mongodb']))
@click.option('--host', required=True)
@click.option('--database', required=True)
@click.option('--username', default=None)
@click.option('--password', default=None)
@click.option('--without-password', default=False)
@click.option('--port', default=None)
@click.option('--compress', default=None, is_flag=True)
@click.option('--format', default=None)
@click.option('--file', required=False, default=None)
def make_backup(name: str, database_type, host, database, username, password, without_password, port, compress, **kwargs):
    name = name.replace('-', '_')

    if without_password is False and password is None:
        password = getpass.getpass('Password: ')

    if without_password is True:
        password = None

    service = BackupsService.build(
        database_type,
        host=host,
        database=database,
        username=username,
        password=password,
        port=port,
    )

    console = Console()
    with console.status("[bold green]Dumping database ..."):
        service.dump(name, compress=compress, **kwargs)
        time.sleep(1)
    console.print("[bold green] Backup created !")


@app.command(name='restore')
@click.option('--database-type', required=True, type=click.Choice(['postgres', 'mongodb']))
@click.option('--host', required=True)
@click.option('--port', default=None)
@click.option('--database', required=True)
@click.option('--username', required=True)
@click.option('--password', default=None)
@click.option('--without-password', default=False)
def restore_backup(database_type, host, port, database, username, password, without_password):
    if without_password is False and password is None:
        password = getpass.getpass('Password: ')

    if without_password is True:
        password = None

    service = BackupsService.build(
        database_type,
        host=host,
        port=port,
        database=database,
        username=username,
        password=password
    )
    console = Console()

    backups = [v for v in BackupsService.list_backups()]
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
