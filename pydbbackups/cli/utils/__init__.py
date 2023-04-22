import json
from importlib import import_module
from typing import Generator, List
from pathlib import Path
from datetime import datetime

from pydbbackups.cli.config import BACKUPS_DATA_DIR, BACKUPS_DIR
from pydbbackups import Backup
from pydbbackups.cli.models import BackupFile, BackupData
from pydbbackups.backups import mongodb, postgres, mysql

databases = {
    'postgres': 'Postgres',
    'mongodb': 'MongoDB',
    'mysql': 'MySQL'
}


def get_backups_data() -> List[BackupData]:
    b_data = BACKUPS_DATA_DIR.read_bytes()
    data = [
        BackupData(
            id=v['id'],
            name=v['name'],
            ext=v['ext'],
            database_name=v['database_name'],
            backup=Path(v['backup']),
            created_at=datetime.fromisoformat(v['created_at'])
        ) for v in json.loads(b_data)
    ]
    return data


def get_backups_files() -> Generator[BackupFile, None, None]:
    for file in BACKUPS_DIR.iterdir():
        [backup_id, name] = file.name.split("___")
        [name, ext] = name.split('.')
        yield BackupFile(id=int(backup_id), name=name, ext=ext, file=file)


def get_backup_class(name: str) -> Backup:
    module = import_module(f"pydbbackups.backups.{name}")
    return getattr(module, databases[name])


def save_backup_file(meta: BackupFile, content: bytes) -> BackupFile:
    if "___" in meta.name:
        raise ValueError("the backup name should not include <___>")

    path = BACKUPS_DIR.joinpath(
        f"{meta.id}___{meta.name}{f'.{meta.ext}' if meta.ext else ''}")
    path.touch()
    path.write_bytes(content)

    return BackupFile(id=meta.id, name=meta.name, ext=meta.ext, file=path)


class DTEncoder(json.JSONEncoder):
    """ Datetime encoder """

    def default(self, o):
        if isinstance(o, datetime):
            return str(o.isoformat())
        if isinstance(o, Path):
            return str(o.resolve())
        return json.JSONEncoder.default(self, o)


# --------- Extension formatters ---------

def mongo_ext_formatter(name: str, **kwargs):
    if not kwargs.get('compress', False):
        return f"{name}.{mongodb.DUMP_DEFAULT_FORMAT}"

    return f"{name}.{mongodb.DUMP_GZIP_FORMAT}"


def postgres_ext_formatter(name, **kwargs):
    dictionary = {
        postgres.DUMP_CUSTOM_FORMAT: 'dump',
        postgres.DUMP_SQL_FORMAT: 'sql',
        postgres.DUMP_TAR_FORMAT: 'tar',
        postgres.DUMP_DIRECTORY_FORMAT: '',
        'DEFAULT': postgres.DUMP_DEFAULT_FORMAT
    }

    backup_format = kwargs.get('format', None)
    if not backup_format:
        ext = dictionary.get(dictionary.get('DEFAULT'))
    else:
        ext = dictionary.get(backup_format)
    return f"{name}{f'.{ext}' if len(ext) > 0 else ''}"


def mysql_ext_formatter(name, **kwargs):
    if kwargs.get('compress', False) is True:
        return f"{name}.{mysql.DUMP_GZIP_FORMAT}"
    return f"{name}.{mysql.DUMP_DEFAULT_FORMAT}"
