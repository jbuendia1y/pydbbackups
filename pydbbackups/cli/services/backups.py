from pydbbackups.cli.utils import get_backup_class, save_backup_file, get_backups_data, get_backups_files, DTEncoder
from pydbbackups.cli.config import BACKUPS_DATA_DIR
from pydbbackups.cli.models import BackupData, BackupFile

from pydbbackups import Backup
from datetime import datetime
from dataclasses import asdict
import json


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
            bdata = next((obj for obj in data if obj.name == bfile.name), None)
            if not bdata:
                continue

            yield bfile, bdata

    def dump(self, name: str, **kwargs):
        output = self.backup_cls.dump(**kwargs)
        if not output:
            return

        created_at = datetime.now()
        meta = save_backup_file(BackupFile(
            name, created_at, ""), output.read())
        print(meta.file, 'Created !')

        data = get_backups_data()
        data.append(BackupData(**{
            "id": len(data),
            "name": name,
            "database_name": self.db_type,
            "created_at": created_at
        }))

        serialized_data = [asdict(v) for v in data]
        BACKUPS_DATA_DIR.write_text(json.dumps(serialized_data, cls=DTEncoder))

    def restore(self):
        self.backup_cls.restore()
