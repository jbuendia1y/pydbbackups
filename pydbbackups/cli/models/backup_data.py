from datetime import datetime
from dataclasses import dataclass, field
from typing import NamedTuple
from pathlib import Path


@dataclass
class BackupData:
    # pylint: disable=C0103
    id: int
    name: str
    ext: str
    backup: Path
    database_name: str
    created_at: datetime = field(default_factory=datetime.now)


class BackupFile(NamedTuple):
    id: int
    name: str
    ext: str
    file: Path
