from dataclasses import dataclass
from typing import Optional, Sequence, Tuple
from io import BytesIO
from pathlib import Path
from pydbbackups.errors import MethodNotImplemented, CommandNotFound
from shutil import which


@dataclass
class Backup:
    host: str
    username: str
    database: str

    uri: Optional[str] = None
    password: Optional[str] = None
    port: Optional[int] = None

    CMDS_TO_CHECK: Optional[Sequence[Tuple[str, Optional[str]] | str]] = None

    @classmethod
    def exist_cmds(cls):
        if not cls.CMDS_TO_CHECK:
            print(
                f"Warning : The {cls.__name__} class doesn't have commands to check")
            return

        for cmd in cls.CMDS_TO_CHECK:
            # args = []
            if isinstance(cmd, tuple):
                command = cmd[0]
                # if len(cmd) > 1:
                #     args = cmd[1]
            else:
                command = cmd

            if not which(command):
                raise CommandNotFound(command)

    def dump(self, **kwargs) -> BytesIO:
        raise MethodNotImplemented('Dump')

    def restore(self, file_path: Path) -> BytesIO:
        raise MethodNotImplemented('Restore')

    def __post_init__(self):
        self.exist_cmds()
