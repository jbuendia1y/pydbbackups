from .base import Backup
import subprocess
from io import BytesIO
from pathlib import Path


DUMP_DEFAULT_FORMAT = "archive"
DUMP_GZIP_FORMAT = "gz"
DUMP_ARCHIVE_FORMAT = "archive"


class MongoDB(Backup):
    CMDS_TO_CHECK = [('mongodump', '--version')]

    def dump(self, **kwargs):
        config = {
            'compress': kwargs.get('compress', False),
        }

        if self.uri:
            args = [
                '-uri', self.uri
            ]
        else:
            args = [
                '--username', self.username,
                '--password', self.password,
                '--host', self.host,
                '--port', f"{self.port}",
                '--db', self.database,
                '--authenticationDatabase', kwargs.get(
                    'authentication_database', 'admin'),
                '--archive'
            ]

        if config['compress']:
            args.append('--gzip')

        p = subprocess.Popen([
            "mongodump",
            *args,
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        status_code = p.wait()
        if status_code > 0:
            raise Exception(p.stderr.read().decode('utf-8'))

        return BytesIO(p.stdout.read())

    def restore(self, file_path: Path) -> BytesIO:
        args = [
            '--username', self.username,
            '--password', self.password,
            '--host', self.host,
            '--port', f"{self.port}",
            '--nsInclude',
            self.database,
        ]

        if file_path.name.endswith(DUMP_GZIP_FORMAT):
            args.append('--gzip')

        args.append(f'--archive={file_path.resolve()}')

        p = subprocess.Popen([
            "mongorestore",
            *args,
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        status_code = p.wait()
        if status_code > 0:
            raise Exception(p.stderr.read().decode('utf-8'))

        return BytesIO(p.stdout.read())
