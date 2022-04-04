from anubis.models import TheiaSession
from anubis.utils.cache import cache
from anubis.utils.data import is_debug


@cache.memoize(timeout=3, unless=is_debug)
def theia_list_all(user_id: str, limit: int = 10):
    """
    list all theia sessions that are currently active. Order by the time
    they were created.

    * Response is lightly cached *

    :param user_id:
    :param limit:
    :return:
    """
    theia_sessions: list[TheiaSession] = (
        TheiaSession.query.filter(
            TheiaSession.owner_id == user_id,
        )
            .order_by(TheiaSession.created.desc())
            .limit(limit)
            .all()
    )

    return [theia_session.data for theia_session in theia_sessions]


@cache.memoize(timeout=1, unless=is_debug)
def theia_poll_ide(theia_session_id: str, user_id: str) -> dict | None:
    """
    Check the status of a theia session. This is called
    when a theia session is created in the frontend. When
    the spinner is going, this function is called until
    the session is active.

    * Response is very lightly cached *

    :param theia_session_id:
    :param user_id:
    :return:
    """

    # Query for the theia session
    theia_session: TheiaSession = TheiaSession.query.filter(
        TheiaSession.id == theia_session_id,
        TheiaSession.owner_id == user_id,
    ).first()

    # If it was not found, then return None
    if theia_session is None:
        return None

    # Else return the session data
    return theia_session.data
