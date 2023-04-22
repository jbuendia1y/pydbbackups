<a href="https://github.com/jbuendia1y/pydbbackups/blob/main/LICENSE"><img src="https://img.shields.io/github/license/jbuendia1y/pydbbackups"></a>
<a href="https://pypi.org/project/pydbbackups/"><img src="https://img.shields.io/pypi/v/pydbbackups"></a>
<a href="https://pypi.org/project/pydbbackups/"><img src="https://img.shields.io/pypi/dw/pydbbackups"></a>
<a href="https://github.com/pylint-dev/pylint"><img src="https://img.shields.io/badge/linting-pylint-yellowgreen"></a>

# PyDBBackups

A backup handler

## Installation

```bash
pip install pydbbackups
```

## CLI example

```bash
dbbackups dump \
    --name backup-example \
    --database-type postgres \
    --host localhost \
    --database test \
    --username postgres \
    --port 5432

# 0__backup-example.sql Created !
```

## Code example

```python
from pydbbackups import Postgres

cls = Postgres(
    database="test",
    host="localhost",
    port=5432,
    username="postgres",
    password="postgres"
)

# In some cases dump method, return None

output = cls.dump()  # Return BytesIO
print(output.read().decode('utf-8'))

```

<p align="center">@jbuendia1y &#60;jbuendia1y@gmail.com&#62;</p>