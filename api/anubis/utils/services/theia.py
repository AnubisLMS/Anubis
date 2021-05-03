from typing import List, Tuple, Union

from werkzeug.utils import redirect

from anubis.config import config
from anubis.models import TheiaSession, User, Config
from anubis.utils.auth import create_token
from anubis.utils.data import is_debug
from anubis.utils.services.cache import cache


@cache.memoize(timeout=5, unless=is_debug)
def get_n_available_sessions() -> Tuple[int, int]:
    """
    Get the number of active sessions and the maximum number of sessions

    :return:
    """
    max_ides_config: Config = Config.query.filter(Config.key == "MAX_IDES").first()
    active_ide_count: int = TheiaSession.query.filter(TheiaSession.active).count()
    max_ides = int(max_ides_config.value) if max_ides_config is not None else 50

    return active_ide_count, max_ides


# @cache.memoize(timeout=60, unless=is_debug)
def theia_redirect_url(theia_session_id: str, netid: str) -> str:
    """
    Generates the url for redirecting to the theia proxy for the given session.

    :param theia_session_id:
    :param netid:
    :return:
    """
    scheme = 'https' if not is_debug() else 'http'

    return "{}://{}/initialize?token={}&anubis=1".format(
        scheme,
        config.THEIA_DOMAIN,
        create_token(netid, session_id=theia_session_id),
    )


def theia_redirect(theia_session: TheiaSession, user: User):
    """
    Create a flask redirect Response for the specified theia session.

    :param theia_session:
    :param user:
    :return:
    """
    return redirect(theia_redirect_url(theia_session.id, user.netid))


@cache.memoize(timeout=3, unless=is_debug)
def theia_list_all(user_id: str, limit: int = 10):
    """
    List all theia sessions that are currently active. Order by the time
    they were created.

    * Response is lightly cached *

    :param user_id:
    :param limit:
    :return:
    """
    theia_sessions: List[TheiaSession] = (
        TheiaSession.query.filter(
            TheiaSession.owner_id == user_id,
        )
            .order_by(TheiaSession.created.desc())
            .limit(limit)
            .all()
    )

    return [theia_session.data for theia_session in theia_sessions]


@cache.memoize(timeout=1, unless=is_debug)
def theia_poll_ide(theia_session_id: str, user_id: str) -> Union[None, dict]:
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
