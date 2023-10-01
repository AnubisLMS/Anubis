import sqlalchemy.sql.sqltypes
from sqlalchemy.dialects import mysql

from anubis.constants import DB_COLLATION, DB_CHARSET
from anubis.env import env


def String(*args, **kwargs) -> mysql.VARCHAR:
    if env.MINDEBUG:
        from sqlalchemy.sql.sqltypes import String as _String

        return _String(*args, **kwargs)
    return mysql.VARCHAR(*args, collation=DB_COLLATION, charset=DB_CHARSET, **kwargs)


def Text(*args, **kwargs) -> mysql.TEXT:
    if env.MINDEBUG:
        from sqlalchemy.sql.sqltypes import Text as _Text

        return _Text(*args, **kwargs)
    return mysql.TEXT(*args, collation=DB_COLLATION, **kwargs)


Enum = sqlalchemy.sql.sqltypes.Enum
DateTime = sqlalchemy.sql.sqltypes.DateTime
Boolean = sqlalchemy.sql.sqltypes.Boolean
JSON = sqlalchemy.sql.sqltypes.JSON
Integer = sqlalchemy.sql.sqltypes.Integer
