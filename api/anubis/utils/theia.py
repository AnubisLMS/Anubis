from typing import List, Tuple

from werkzeug.utils import redirect

from anubis.config import config
from anubis.models import TheiaSession, User, Config
from anubis.utils.auth import get_token
from anubis.utils.cache import cache


@cache.memoize(timeout=5)
def get_n_available_sessions() -> Tuple[int, int]:
    """
    Get the number of active sessions and the maximum number of sessions

    :return:
    """
    max_ides_config: Config = Config.query.filter(
        Config.key == "MAX_IDES"
    ).first()

    active_ide_count: int = TheiaSession.query.filter(
        TheiaSession.active == True
    ).count()

    max_ides = int(max_ides_config.value) if max_ides_config is not None else 50

    return active_ide_count, max_ides


# @cache.memoize(timeout=60 * 5)
def theia_redirect_url(theia_session_id: int, netid: str) -> str:
    """
    Generates the url for redirecting to the theia proxy for the given session.

    :param theia_session_id:
    :param netid:
    :return:
    """
    return "https://{}/initialize?token={}&anubis=1".format(
        config.THEIA_DOMAIN,
        get_token(netid, session_id=theia_session_id),
    )


def theia_redirect(theia_session: TheiaSession, user: User):
    return redirect(theia_redirect_url(theia_session.id, user.netid))


@cache.memoize(timeout=1)
def theia_list_all(user_id: int, limit: int = 10):
    theia_sessions: List[TheiaSession] = TheiaSession.query.filter(
        TheiaSession.owner_id == user_id,
    ).order_by(TheiaSession.created.desc()).limit(limit).all()

    return [
        theia_session.data
        for theia_session in theia_sessions
    ]


@cache.memoize(timeout=1)
def theia_poll_ide(theia_session_id: int, user_id: int):
    theia_session = TheiaSession.query.filter(
        TheiaSession.id == theia_session_id,
        TheiaSession.owner_id == user_id,
    ).first()

    if theia_session is None:
        return None

    return theia_session.data
