"""
PyDBBackups

example:

```.py
from pydbbackups import Postgres

cls = Postgres(
    database="test",
    host="localhost",
    port=5432,
    username="postgres",
    password="postgres"
)

# In some cases dump method, return None

output = cls.dump() # Return BytesIO
print(output.read().decode('utf-8'))
```
"""

from .backups import *
