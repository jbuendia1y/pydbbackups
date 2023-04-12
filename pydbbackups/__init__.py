"""
PyDBBackups

example:

```.py
from pydbbackups import Postgres

cls = Postgres(
    compress=False,
    database="test",
    host="localhost",
    port=5432,
    username="postgres",
    password="postgres"
)

# In some cases dump method, return None
# Like MongoDB

output = cls.dump() # Return BytesIO
print(output.read().decode('utf-8'))
```
"""

from .backups import *
