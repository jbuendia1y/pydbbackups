import json
from importlib import import_module
from typing import Generator, List
from pathlib import Path

from pydbbackups.cli.config import BACKUPS_DATA_DIR, BACKUPS_DIR
from pydbbackups import Backup
from pydbbackups.cli.models import BackupFile, BackupData
from datetime import datetime
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
    dir = BACKUPS_DIR.iterdir()

    for f in dir:
        [id, name] = f.name.split("___")
        [name, ext] = name.split('.')
        yield BackupFile(id=int(id), name=name, ext=ext, file=f)


def get_backup_class(name: str) -> Backup:
    m = import_module(f"pydbbackups.backups.{name}")
    return getattr(m, databases[name])


def save_backup_file(meta: BackupFile, content: bytes | str) -> BackupFile:
    if "___" in meta.name:
        raise ValueError("the backup name should not include <___>")

    path = BACKUPS_DIR.joinpath(
        f"{meta.id}___{meta.name}{f'.{meta.ext}' if meta.ext else ''}")
    path.touch()
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)

    return BackupFile(id=meta.id, name=meta.name, ext=meta.ext, file=path)


class DTEncoder(json.JSONEncoder):
    """ Datetime encoder """

    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj.isoformat())
        if isinstance(obj, Path):
            return str(obj.resolve())
        return json.JSONEncoder.default(self, obj)


# --------- Extension formatters ---------

def mongo_ext_formatter(name: str, **kwargs):
    if not kwargs.get('compress', False):
        return f"{name}.{mongodb.DUMP_DEFAULT_FORMAT}"
    else:
        return f"{name}.{mongodb.DUMP_GZIP_FORMAT}"


def postgres_ext_formatter(name, **kwargs):
    dictionary = {
        postgres.DUMP_CUSTOM_FORMAT: 'dump',
        postgres.DUMP_SQL_FORMAT: 'sql',
        postgres.DUMP_TAR_FORMAT: 'tar',
        postgres.DUMP_DIRECTORY_FORMAT: '',
        'DEFAULT': postgres.DUMP_DEFAULT_FORMAT
    }

    format = kwargs.get('format', None)
    if not format:
        ext = dictionary.get(dictionary.get('DEFAULT'))
    else:
        ext = dictionary.get(format)
    return f"{name}{f'.{ext}' if len(ext) > 0 else ''}"


def mysql_ext_formatter(name, **kwargs):
    if kwargs.get('compress', False) is True:
        return f"{name}.{mysql.DUMP_GZIP_FORMAT}"
    else:
        return f"{name}.{mysql.DUMP_DEFAULT_FORMAT}"
