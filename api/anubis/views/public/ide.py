from datetime import datetime, timedelta
from typing import Dict

from flask import Blueprint, redirect

from anubis.models import User, TheiaSession, db, Assignment, AssignmentRepo
from anubis.utils.auth import current_user, require_user
from anubis.utils.decorators import json_response, load_from_id
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import error_response, success_response
from anubis.utils.redis_queue import enqueue_ide_stop, enqueue_ide_initialize
from anubis.utils.theia import (
    theia_redirect_url,
    get_n_available_sessions,
    theia_list_all,
    theia_poll_ide,
    theia_redirect,
)

ide = Blueprint("public-ide", __name__, url_prefix="/public/ide")


@ide.route("/list")
@log_endpoint("ide-list")
@require_user()
@json_response
def public_ide_list():
    """
    List all sessions, active and inactive

    :return:
    """
    user: User = current_user()

    active_count, max_count = get_n_available_sessions()

    return success_response({
        "session_available": active_count < max_count,
        "sessions": theia_list_all(user.id),
    })


@ide.route("/available")
@log_endpoint("ide-available")
@require_user()
@json_response
def public_ide_available():
    """
    List all sessions, active and inactive

    :return:
    """
    active_count, max_count = get_n_available_sessions()

    return success_response({
        "session_available": active_count < max_count,
    })


@ide.route("/active/<string:assignment_id>")
@log_endpoint("ide-active")
@require_user()
@json_response
def public_ide_active(assignment_id):
    """
    List all sessions, active and inactive

    :return:
    """
    user = current_user()

    session = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.owner_id == user.id,
        TheiaSession.assignment_id == assignment_id,
    ).first()

    if session is None:
        return success_response({"active": None})

    return success_response({
        "session": session.data
    })


@ide.route("/stop/<string:theia_session_id>")
@log_endpoint("stop-theia-session")
@require_user()
def public_ide_stop(theia_session_id: str) -> Dict[str, str]:
    user: User = current_user()

    theia_session: TheiaSession = TheiaSession.query.filter(
        TheiaSession.id == theia_session_id,
        TheiaSession.owner_id == user.id,
    ).first()
    if theia_session is None:
        return error_response("Can not find session.")

    theia_session.active = False
    theia_session.ended = datetime.now()
    theia_session.state = "Ending"
    db.session.commit()

    enqueue_ide_stop(theia_session.id)

    return success_response({
        'status': 'Session stopped.',
        'variant': 'warning',
    })


@ide.route("/poll/<string:theia_session_id>")
@log_endpoint("ide-poll-id", lambda: "ide-poll")
@require_user()
@json_response
def public_ide_poll(theia_session_id: str) -> Dict[str, str]:
    """
    Slightly cached endpoint for polling for session data.

    :param theia_session_id:
    :return:
    """
    user: User = current_user()

    session_data = theia_poll_ide(theia_session_id, user.id)
    if session_data is None:
        return error_response("Can not find session")

    return success_response({
        "loading": session_data['state'] == 'Initializing',
        "session": session_data,
    })


@ide.route("/redirect-url/<string:theia_session_id>")
@log_endpoint("ide-redirect-url", lambda: "ide-redirect-url")
@require_user()
@json_response
def public_ide_redirect_url(theia_session_id: str) -> Dict[str, str]:
    """
    Get the redirect url for a given session

    :param theia_session_id:
    :return:
    """
    user: User = current_user()

    theia_session: TheiaSession = TheiaSession.query.filter(
        TheiaSession.id == theia_session_id,
        TheiaSession.owner_id == user.id,
    ).first()
    if theia_session is None:
        return error_response("Can not find session")

    return success_response(
        {"redirect": theia_redirect_url(theia_session.id, user.netid)}
    )


@ide.route("/initialize/<string:id>")
@log_endpoint("ide-initialize", lambda: "ide-initialize")
@require_user()
@load_from_id(Assignment, verify_owner=False)
def public_ide_initialize(assignment: Assignment):
    """
    Redirect to theia proxy.

    :param assignment:
    :return:
    """
    user: User = current_user()

    if not assignment.ide_enabled:
        return error_response("Theia not enabled for this assignment.")

    # Check for existing active session
    active_session = (
        TheiaSession.query.join(Assignment)
        .filter(
            TheiaSession.owner_id == user.id,
            TheiaSession.assignment_id == assignment.id,
            TheiaSession.active == True,
            Assignment.release_date <= datetime.now(),
            Assignment.due_date + timedelta(days=7) >= datetime.now(),
        )
        .first()
    )
    if active_session is not None:
        return success_response({
            "active": active_session.active,
            "session": active_session.data
        })

    if datetime.now() <= assignment.release_date:
        return error_response('Assignment has not been released.')

    if assignment.due_date + timedelta(days=3 * 7) <= datetime.now():
        return error_response("Assignment due date passed over 3 weeks ago.")

    # Make sure we have a repo we can use
    repo = AssignmentRepo.query.filter(
        AssignmentRepo.owner_id == user.id,
        AssignmentRepo.assignment_id == assignment.id,
    ).first()
    if repo is None:
        return redirect(
            "/courses/assignments?error=Please create your assignment repo first."
        )

    # Create a new session
    session = TheiaSession(
        owner_id=user.id,
        assignment_id=assignment.id,
        repo_id=repo.id,
        active=True,
        state="Initializing",
    )
    db.session.add(session)
    db.session.commit()

    # Send kube resource initialization rpc job
    enqueue_ide_initialize(session.id)

    # Redirect to proxy
    return success_response({
        "active": session.active,
        "session": session.data,
        "status": 'Session created',
    })
