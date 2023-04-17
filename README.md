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