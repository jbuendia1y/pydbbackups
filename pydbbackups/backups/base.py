from dataclasses import dataclass
from typing import Optional, Sequence, Tuple
from io import BytesIO
from pathlib import Path
from shutil import which
from pydbbackups.errors import MethodNotImplemented, CommandNotFound


@dataclass
class Backup:
    host: str
    username: str
    database: str

    uri: Optional[str] = None
    password: Optional[str] = None
    port: Optional[int] = None

    cmds_to_check: Optional[Sequence[Tuple[str, Optional[str]] | str]] = None

    @classmethod
    def exist_cmds(cls):
        if not cls.cmds_to_check:
            print(
                f"Warning : The {cls.__class__.__name__} class doesn't have commands to check")
            return
        # pylint: disable=E1133
        for cmd in cls.cmds_to_check:
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
        """ Generates a backup """
        raise MethodNotImplemented('Dump')

    def restore(self, file_path: Path) -> BytesIO:
        """ Restore a backup """
        raise MethodNotImplemented('Restore')

    def __post_init__(self):
        self.exist_cmds()
