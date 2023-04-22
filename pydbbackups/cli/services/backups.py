import json
from dataclasses import asdict
from pathlib import Path
from datetime import datetime

from pydbbackups.cli.utils import (
    get_backup_class,
    save_backup_file,
    get_backups_data,
    get_backups_files,
    DTEncoder,
    mongo_ext_formatter,
    postgres_ext_formatter,
    mysql_ext_formatter
)
from pydbbackups.cli.config import BACKUPS_DATA_DIR
from pydbbackups.cli.models import BackupData, BackupFile
from pydbbackups import Backup


def backup_ext_formatter(db_type: str, name: str, **kwargs) -> str:
    databases = {
        "postgres": postgres_ext_formatter,
        "mongodb": mongo_ext_formatter,
        "mysql": mysql_ext_formatter
    }

    formatter = databases.get(db_type, None)

    if not formatter:
        return name

    return formatter(name, **kwargs)


class BackupsService:
    backup_cls: Backup
    db_type: str

    def __init__(self, backup_cls: Backup = None) -> None:
        self.backup_cls = backup_cls

    @staticmethod
    def build(db_type: str, **kwargs):
        backup_cls = get_backup_class(db_type)(**kwargs)
        cls = BackupsService(backup_cls)
        cls.db_type = db_type

        return cls

    @staticmethod
    def list_backups():
        data = get_backups_data()
        backups = get_backups_files()

        for bfile in backups:
            # Get the first object
            bdata = next((obj for obj in data if obj.id == bfile.id), None)
            if not bdata:
                continue

            yield bfile, bdata

    @staticmethod
    def get_backup(backup_id: int):
        data = get_backups_data()
        for value in data:
            if value.id == backup_id:
                return value
        return None

    def dump(self, name: str, **kwargs):
        output = self.backup_cls.dump(**kwargs)
        content = output.read()

        data = get_backups_data()
        created_id = len(data)
        created_at = datetime.now()

        name = backup_ext_formatter(
            self.db_type, name, **kwargs)

        if len(name.split('.')) > 1:
            [name, ext] = name.split('.')

        if not output or len(content) == 0:
            print('Warning: This backup will not be saved')
            return

        meta = save_backup_file(BackupFile(
            id=created_id, name=name, ext=ext, file=Path()), content)
        print(meta.file, 'Created !')

        data.append(BackupData(**{
            "id": len(data),
            "name": meta.name,
            "ext": meta.ext,
            "database_name": self.db_type,
            "backup": meta.file,
            "created_at": created_at
        }))

        serialized_data = [asdict(v) for v in data]
        BACKUPS_DATA_DIR.write_text(json.dumps(
            serialized_data, cls=DTEncoder), encoding='utf-8')

    def restore(self, backup: Path):
        self.backup_cls.restore(backup)
