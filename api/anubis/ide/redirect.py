from werkzeug.utils import redirect

from anubis.models import TheiaSession, User
from anubis.utils.auth.token import create_token


def theia_redirect_url(theia_session_id: str, netid: str) -> str:
    """
    Generates the url for redirecting to the theia proxy for the given session.

    :param theia_session_id:
    :param netid:
    :return:
    """
    return "/ide/initialize?token={}&anubis=1".format(
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