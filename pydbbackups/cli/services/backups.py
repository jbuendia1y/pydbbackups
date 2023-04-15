from pydbbackups.cli.utils import get_backup_class, save_backup_file, get_backups_data, get_backups_files, DTEncoder
from pydbbackups.cli.config import BACKUPS_DATA_DIR
from pydbbackups.cli.models import BackupData, BackupFile

from pydbbackups import Backup
from datetime import datetime
from dataclasses import asdict
from pydbbackups.backups import postgres, mongodb
import json
from pathlib import Path


def backup_ext_formatter(db_type: str, name: str, format: str = None) -> str:
    databases = {
        "postgres": {
            postgres.DUMP_CUSTOM_FORMAT: 'dump',
            postgres.DUMP_SQL_FORMAT: 'sql',
            postgres.DUMP_TAR_FORMAT: 'tar',
            postgres.DUMP_DIRECTORY_FORMAT: '',
            'DEFAULT': postgres.DUMP_DEFAULT_FORMAT
        },
        "mongodb": {
            mongodb.DUMP_ARCHIVE_FORMAT: 'archive',
            mongodb.DUMP_GZIP_FORMAT: 'gz',
            'DEFAULT': mongodb.DUMP_DEFAULT_FORMAT
        }
    }

    dictionary = databases.get(db_type, None)

    if not dictionary:
        return name

    if not format:
        ext = dictionary.get(dictionary.get('DEFAULT'))
    else:
        ext = dictionary.get(format)
    return f"{name}{f'.{ext}' if len(ext) > 0 else ''}"


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

    def dump(self, name: str, **kwargs):
        output = self.backup_cls.dump(**kwargs)
        content = output.read()

        data = get_backups_data()
        created_id = len(data)
        created_at = datetime.now()

        name = backup_ext_formatter(
            self.db_type, name, kwargs.get('format', None))

        if len(name.split('.')) > 1:
            [name, ext] = name.split('.')

        if not output or len(content) == 0:
            print('Warning: This backup not to be save')
            return
        else:
            meta = save_backup_file(BackupFile(
                id=created_id, name=name, ext=ext, file=Path()), content)
            print(meta.file, 'Created !')

        data.append(BackupData(**{
            "id": len(data),
            "name": meta.name,
            "ext": meta.ext,
            "database_name": self.db_type,
            "created_at": created_at
        }))

        serialized_data = [asdict(v) for v in data]
        BACKUPS_DATA_DIR.write_text(json.dumps(serialized_data, cls=DTEncoder))

    def restore(self):
        self.backup_cls.restore()
