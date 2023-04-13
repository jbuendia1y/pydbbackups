from pathlib import Path
from .base import Backup
import subprocess
import gzip
import os
from io import BytesIO


class Postgres(Backup):

    CMDS_TO_CHECK = [
        ('pg_dump', '--version'),
        ('pg_restore', '--version'),
        ('psql', '--version')]

    def dump(self) -> BytesIO:
        # host = f"-h {self.host}"
        # username = f"-U {self.username}"
        # database = self.database
        # password = f'PGPASSWORD="{self.password}"' if self.password else None

        # cmd = f"{password + ' ' if password else ''} pg_dump {host} {username} {database} {'-w' if password else '--no-password'}"

        env = os.environ.copy()
        if self.password:
            env['PGPASSWORD'] = self.password

        p = subprocess.Popen([
            'pg_dump',
            '-h',
            self.host,
            '-U',
            self.username,
            self.database,
            '-w' if self.password else '--no-password'
        ], env=env, stdout=subprocess.PIPE)

        code = p.wait()
        if code > 0:
            print(p.stderr)
            raise Exception(p.stderr.read().decode('utf-8'))

        if self.compress:
            compressed = gzip.compress(p.stdout, compresslevel=9)
            return BytesIO(compressed)

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
