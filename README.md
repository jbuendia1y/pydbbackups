# PyDBBackups

A backup handler

## Installation

```bash
pip install pydbbackups
```

## CLI example

```bash
dbbackups run \
    --name backup-example \
    --database-type postgres \
    --host localhost \
    --database test \
    --username postgres \
    --port 5432

# backup-example___2023-04-10 11:42:59.090131 Created !
```

## Code example

```python
from pydbbackups import Postgres

cls = Postgres(
    name="MyDB",
    compress=False,
    database="test",
    host="localhost",
    port=5432,
    username="postgres",
    password="postgres"
)

# In some cases dump method, return None
# Like MongoDB

output = cls.dump()  # Return BytesIO
print(output.read().decode('utf-8'))

```

<p align="center">@jbuendia1y &#60;jbuendia1y@gmail.com&#62;</p>