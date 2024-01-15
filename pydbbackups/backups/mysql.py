from io import BytesIO
from pathlib import Path
import subprocess
import gzip
import os
from pydbbackups.errors import CMDExecutionError
from .base import Backup

DUMP_DEFAULT_FORMAT = "sql"
DUMP_SQL_FORMAT = "sql"
DUMP_GZIP_FORMAT = "gz"


class MySQL(Backup):
    cmds_to_check = [('mysqldump', '--version'), ('mysql', '--version')]

    def dump(self, **kwargs) -> BytesIO:
        env = os.environ.copy()
        env['MYSQL_PWD'] = self.password

        args = [
            '--quick',
            f'--host={self.host}',
            f'--port={self.port}',
            f"--user={self.username}",
            '--databases',
            self.database,
            '--force'
        ]

        with subprocess.Popen(
            [
                'mysqldump',
                *args
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process:
            status_code = process.wait()

            if status_code > 0:
                error = process.stderr.read().decode('utf-8')
                raise CMDExecutionError(error)

            output = BytesIO(process.stdout.read())

        if kwargs.get('compress') is True:
            output = BytesIO(gzip.compress(output.read()))

        return output

    def restore(self, file_path: Path) -> BytesIO:
        env = os.environ.copy()
        env['MYSQL_PWD'] = self.password

        args = [
            '-h',
            self.host,
            '-P',
            f"{self.port}",
            '-u',
            self.username,
            '-e'
        ]

        if file_path.name.endswith(DUMP_GZIP_FORMAT):
            sql_content = gzip.decompress(file_path.resolve().read_bytes())
            backup = sql_content.decode('utf-8')
        else:
            backup = f'source {file_path.resolve()}'

        args.append(backup)

        with subprocess.Popen(
            [
                'mysql',
                *args
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ) as process:
            status_code = process.wait()

            if status_code > 0:
                error = process.stderr.read().decode('utf-8')
                raise CMDExecutionError(error)
