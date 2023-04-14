from pathlib import Path
from .base import Backup
import subprocess
import os
from io import BytesIO

DUMP_SQL_FORMAT = 'p'
DUMP_CUSTOM_FORMAT = 'c'
DUMP_DIRECTORY_FORMAT = 'd'
DUMP_TAR_FORMAT = 't'


class Postgres(Backup):

    CMDS_TO_CHECK = [
        ('pg_dump', '--version'),
        ('pg_restore', '--version'),
        ('psql', '--version')]

    def dump(self, **kwargs) -> BytesIO:
        env = os.environ.copy()
        if self.password:
            env['PGPASSWORD'] = self.password

        config = {
            "format": kwargs.get('format', DUMP_SQL_FORMAT),
            "compress": kwargs.get('compress', False),
            "compress_level": kwargs.get('compress_level', 9),
            "file": kwargs.get('file', None)
        }

        config_list = [
            "-F",
            config['format'],
            "-Z",
            str(config['compress_level'] if config['compress'] else 0),
        ]

        if not config['format'] == DUMP_SQL_FORMAT and not config['format'] == DUMP_CUSTOM_FORMAT and not config['format'] == DUMP_TAR_FORMAT:
            config_list.append('-f')
            if not config['file']:
                raise ValueError('The output format need file kwarg')
            config_list.append(str(Path(config['file']).resolve()))

        p = subprocess.Popen([
            'pg_dump',
            '-h',
            self.host,
            '-U',
            self.username,
            '-p',
            f"{self.port}",
            self.database,
            '-w' if self.password else '--no-password',
            *config_list
        ], env=env, stdout=subprocess.PIPE)

        code = p.wait()
        if code > 0:
            raise Exception(p.stderr.read().decode('utf-8'))

        return BytesIO(p.stdout.read())

    def restore(self, file_path: Path) -> BytesIO:
        env = os.environ.copy()
        if self.password:
            env['PGPASSWORD'] = self.password

        args = [
            '-h',
            self.host,
            '-p',
            f"{self.port}",
            '-U',
            self.username,
            '-d',
            self.database,
        ]

        f_arg = [
            '-f',
            f"{file_path.absolute()}",
        ] if str(file_path).endswith('.sql') else [
            f"{file_path.absolute()}",
        ]

        p = subprocess.Popen([
            'psql' if str(file_path).endswith('.sql') else 'pg_restore',
            *args,
            *f_arg
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        code = p.wait()
        if code > 0:
            print(p.stderr)
            raise Exception(p.stderr.read().decode('utf-8'))
