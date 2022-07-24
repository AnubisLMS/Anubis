import uuid

from sqlalchemy import Column

from anubis.models.sqltypes import String

default_id_length = 36


def default_id_factory() -> str:
    return str(uuid.uuid4())


def default_id(*args, primary_key=True, index=True, default=default_id_factory, **kwargs) -> Column:
    return Column(
        *args,
        String(length=default_id_length),
        primary_key=primary_key,
        index=index,
        default=default,
        **kwargs,
    )
