from datetime import datetime

from anubis.models import TheiaSession


def mark_session_ended(theia_session: TheiaSession):
    """
    Mark the database entries for the
    theia session as ended.

    :param theia_session:
    :return:
    """
    theia_session.active = False
    theia_session.state = "Ended"
    theia_session.ended = datetime.now()