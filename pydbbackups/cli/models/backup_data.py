from datetime import datetime
from dataclasses import dataclass, field
from collections import namedtuple


@dataclass
class BackupData:
    id: int
    name: str
    database_name: str
    created_at: datetime = field(default_factory=lambda: datetime.now())


BackupFile = namedtuple('BackupFile', ['name', 'date', 'file'])
