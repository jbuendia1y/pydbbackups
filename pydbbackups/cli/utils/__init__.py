import json
from importlib import import_module
from typing import Generator, List

from pydbbackups.cli.config import BACKUPS_DATA_DIR, BACKUPS_DIR
from pydbbackups import Backup
from pydbbackups.cli.models import BackupFile, BackupData
from datetime import datetime

databases = {
    'postgres': 'Postgres',
    'mongodb': 'MongoDB'
}


def get_backups_data() -> List[BackupData]:
    b_data = BACKUPS_DATA_DIR.read_bytes()
    data = [BackupData(**v) for v in json.loads(b_data)]
    return data


def get_backups_files() -> Generator[BackupFile, None, None]:
    dir = BACKUPS_DIR.iterdir()

    for f in dir:
        [name, date] = f.name.split("___")
        yield BackupFile(name, date, f)


def get_backup_class(name: str) -> Backup:
    m = import_module(f"pydbbackups.backups.{name}")
    return getattr(m, databases[name])


def save_backup_file(meta: BackupFile, content: bytes | str) -> BackupFile:
    if "___" in meta.name:
        raise ValueError("the backup name should not include <___>")
    path = BACKUPS_DIR.joinpath(f"{meta.name}___{meta.date}")
    path.touch()
    if content is bytes:
        path.write_bytes(content)
    else:
        path.write_text(content)

    return BackupFile(meta.name, meta.date, path)


class DTEncoder(json.JSONEncoder):
    """ Datetime encoder """

    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
