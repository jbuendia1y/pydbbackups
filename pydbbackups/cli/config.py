from pathlib import Path

APP_DIR = Path().home().joinpath('pydbbackups').absolute()

BACKUPS_DIR = APP_DIR.joinpath('backups')
BACKUPS_DATA_DIR = APP_DIR.joinpath('backups.json')


def build_config():
    APP_DIR.mkdir(exist_ok=True, parents=True)
    BACKUPS_DIR.mkdir(exist_ok=True, parents=True)

    if not BACKUPS_DATA_DIR.exists():
        BACKUPS_DATA_DIR.touch()
        BACKUPS_DATA_DIR.write_text('[]', encoding='utf-8')

    BACKUPS_DATA_DIR.touch(exist_ok=True)
