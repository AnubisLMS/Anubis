from anubis.models import User, TheiaSession
from anubis.utils.cache import cache
from anubis.utils.config import get_config_int
from anubis.utils.data import is_debug


@cache.memoize(timeout=5, source_check=True)
def get_recent_sessions(user_id: str, limit: int = 10, offset: int = 10) -> list[dict]:
    student = User.query.filter(
        User.id == user_id,
    ).first()

    sessions: list[TheiaSession] = (
        TheiaSession.query.filter(
            TheiaSession.owner_id == student.id,
        )
            .order_by(TheiaSession.created.desc())
            .limit(limit)
            .offset(offset)
            .all()
    )

    return [session.data for session in sessions]


@cache.memoize(timeout=5, unless=is_debug)
def get_n_available_sessions() -> tuple[int, int]:
    """
    Get the number of active sessions and the maximum number of sessions

    :return:
    """
    max_ides = get_config_int("THEIA_MAX_SESSIONS", default=50)
    active_ide_count: int = TheiaSession.query.filter(TheiaSession.active).count()

    return active_ide_count, max_ides
