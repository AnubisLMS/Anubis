from anubis.utils.data import with_context
from anubis.utils.testing.seed import seed as _seed


@with_context
def seed():
    _seed()
