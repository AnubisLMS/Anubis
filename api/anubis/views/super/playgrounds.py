from typing import List

from datetime import datetime
from flask import Blueprint

from anubis.lms.theia import initialize_ide, assert_theia_sessions_enabled
from anubis.models import db, TheiaSession, TheiaImage
from anubis.utils.auth.http import require_superuser
from anubis.utils.auth.user import current_user
from anubis.utils.http import success_response
from anubis.utils.http.decorators import json_response, load_from_id
from anubis.utils.data import req_assert
from anubis.rpc.theia import reap_theia_playgrounds_all
from anubis.utils.rpc import enqueue_ide_stop, rpc_enqueue

playgrounds_ = Blueprint("super-playgrounds", __name__, url_prefix="/super/playgrounds")


@playgrounds_.route("/list")
@require_superuser()
@json_response
def super_playgrounds_list():
    """
    List all active ide sessions

    :return:
    """

    # Get all active sessions
    sessions = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.playground == True,
    ).all()

    # Hand back response
    return success_response({"sessions": [session.data for session in sessions]})


@playgrounds_.route("/stop/<string:id>")
@require_superuser()
@json_response
def super_playgrounds_stop_id(id: str):
    """
    Stop a specific IDE

    :return:
    """

    # Search for the theia session
    session = TheiaSession.query.filter(
        TheiaSession.id == id,
    ).first()

    # Verify it exists
    req_assert(session is not None, message="session does not exist")

    # Set all the things as stopped
    session.active = False
    session.ended = datetime.now()
    session.state = "Ending"

    # Commit the stop
    db.session.commit()

    # Enqueue the theia stop cleanup
    enqueue_ide_stop(session.id)

    # Hand back response
    return success_response({"status": "Session Killed."})


@playgrounds_.route("/reap-all")
@require_superuser()
@json_response
def super_playgrounds_stop_all():
    """
    Enqueue a job for the rpc workers to reap all the active
    theia submissions. They will end all active sessions in the
    database, then schedule all the kube resources for deletion.

    :return:
    """

    # Send reap job to rpc cluster
    rpc_enqueue(reap_theia_playgrounds_all, "theia")

    # Hand back status
    return success_response({"status": "Reap job enqueued. Session cleanup will take a minute."})
