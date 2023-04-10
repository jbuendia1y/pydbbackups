from .base import Backup
import subprocess


class MongoDB(Backup):
    CMDS_TO_CHECK = [('mongodump', '--version')]

    def dump(self):
        if self.uri:
            args = [
                '-uri', self.uri
            ]
        else:
            args = [
                '--out=mongodb_dump',
                '--username', self.username,
                '--password', self.password,
                '--host', self.host,
                '--port', f"{self.port}",
            ]

        if self.compress:
            args.append('--gzip')

        p = subprocess.Popen([
            "mongodump",
            *args
        ])

        status_code = p.wait()
        if status_code > 0:
            raise Exception(p.stderr.read().decode('utf-8'))

        return p.stdout
