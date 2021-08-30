import copy
from datetime import datetime, timedelta
from typing import Dict

from flask import Blueprint, request

from anubis.models import TheiaSession, db, Assignment, AssignmentRepo
from anubis.utils.auth.http import require_user
from anubis.utils.auth.user import current_user
from anubis.utils.data import req_assert
from anubis.utils.http.decorators import json_response, load_from_id
from anubis.utils.http.https import error_response, success_response
from anubis.utils.lms.courses import is_course_admin
from anubis.utils.lms.theia import (
    theia_redirect_url,
    get_n_available_sessions,
    theia_poll_ide,
)
from anubis.utils.services.rpc import enqueue_ide_stop, enqueue_ide_initialize

ide = Blueprint("public-ide", __name__, url_prefix="/public/ide")


@ide.route("/available")
@require_user()
@json_response
def public_ide_available():
    """
    List all sessions, active and inactive

    :return:
    """

    # Get the active and maximum number of ides currently allocated
    active_count, max_count = get_n_available_sessions()

    # Calculate if sessions are available
    session_available: bool = active_count < max_count

    # pass back if sessions are available
    return success_response({
        "session_available": session_available,
    })


@ide.route("/active/<string:assignment_id>")
@require_user()
@json_response
def public_ide_active(assignment_id):
    """
    List all sessions, active and inactive

    :return:
    """

    # Find if they have an active session for this assignment
    session = TheiaSession.query.filter(
        TheiaSession.active,
        TheiaSession.owner_id == current_user.id,
        TheiaSession.assignment_id == assignment_id,
    ).first()

    # If they do not have an active assignment, then pass back False
    if session is None:
        return success_response({"active": False})

    # If they do have a session, then pass back True
    return success_response({
        "active": True,
        "session": session.data,
    })


@ide.route("/stop/<string:theia_session_id>")
@require_user()
def public_ide_stop(theia_session_id: str) -> Dict[str, str]:
    """
    Endpoint for users to request a stop of their IDE. We need to mark the
    IDE as stopped in the database, and enqueue a job to clean up the
    existing kubernetes resources.

    :param theia_session_id:
    :return:
    """

    # Find the theia session
    theia_session: TheiaSession = TheiaSession.query.filter(
        TheiaSession.id == theia_session_id,
        TheiaSession.owner_id == current_user.id,
    ).first()

    # Verify that the session exists
    req_assert(theia_session is not None, message='session does not exist')

    # Mark the session as stopped.
    theia_session.active = False
    theia_session.ended = datetime.now()
    theia_session.state = "Ended"

    # Commit the change
    db.session.commit()

    # Enqueue a ide stop job
    enqueue_ide_stop(theia_session.id)

    # Pass back the status
    return success_response({
        "status": "Session stopped.",
        "variant": "warning",
    })


@ide.route("/poll/<string:theia_session_id>")
@require_user()
@json_response
def public_ide_poll(theia_session_id: str) -> Dict[str, str]:
    """
    Slightly cached endpoint for polling for session data.

    :param theia_session_id:
    :return:
    """

    # Find the (possibly cached) session data
    session_data = theia_poll_ide(theia_session_id, current_user.id)

    # Assert that the session exists
    req_assert(session_data is not None, message='session does not exist')

    # Check to see if it is still initializing
    loading = session_data["state"] not in {"Running", "Ended", "Failed"}

    # Pass back the status and data
    return success_response({
        "loading": loading,
        "session": session_data,
        "status": "Session is now ready." if not loading else None,
    })


@ide.route("/redirect-url/<string:theia_session_id>")
@require_user()
@json_response
def public_ide_redirect_url(theia_session_id: str) -> Dict[str, str]:
    """
    Get the redirect url for a given session

    :param theia_session_id:
    :return:
    """

    # Search for session
    theia_session: TheiaSession = TheiaSession.query.filter(
        TheiaSession.id == theia_session_id,
        TheiaSession.owner_id == current_user.id,
    ).first()

    # Verify that the session exists
    req_assert(theia_session is not None, message='session does not exist')

    # Pass back redirect link
    return success_response({
        "redirect": theia_redirect_url(theia_session.id, current_user.netid)
    })


@ide.route("/initialize/<string:id>")
@require_user()
@load_from_id(Assignment, verify_owner=False)
def public_ide_initialize(assignment: Assignment):
    """
    Redirect to theia proxy.

    :param assignment:
    :return:
    """

    # verify that ides are enabled for this assignment
    req_assert(assignment.ide_enabled, message='IDEs are not enabled for this assignment')

    # Check for existing active session
    active_session = TheiaSession.query.join(Assignment).filter(
        TheiaSession.owner_id == current_user.id,
        TheiaSession.assignment_id == assignment.id,
        TheiaSession.active,
    ).first()

    # If there was an existing session for this assignment found, skip
    # the initialization, and return the active session information.
    if active_session is not None:
        return success_response({
            "active": active_session.active,
            "session": active_session.data
        })

    # If it is a student (not a ta) requesting the ide, then we will need to
    # make sure that the assignment has actually been released.
    if not is_course_admin(assignment.course_id):

        # If the assignment has been released, then we cannot allocate a session to a student
        req_assert(assignment.release_date < datetime.now(), message="Assignment has not been released")

        # If 3 weeks has passed since the assignment has been due, then we should not allow
        # new sessions to be created
        if assignment.due_date + timedelta(days=3 * 7) <= datetime.now():
            return error_response("Assignment due date passed over 3 weeks ago.")

    # If github repos are enabled for this assignment, then we will
    # need to get the repo url.
    repo_url: str = ''
    if assignment.github_repo_required:

        # Make sure github username is set
        req_assert(current_user.github_username is not None, message='Please set github username')

        # Make sure we have a repo we can use
        repo: AssignmentRepo = AssignmentRepo.query.filter(
            AssignmentRepo.owner_id == current_user.id,
            AssignmentRepo.assignment_id == assignment.id,
        ).first()

        # Verify that the repo exists
        req_assert(
            repo is not None,
            message='Anubis can not find your assignment repo. '
                    'Please make sure your github username is set and is correct.'
        )
        # Update the repo url
        repo_url = repo.repo_url

    # Create the theia options from the assignment default
    options = copy.deepcopy(assignment.theia_options)

    # Figure out options from user values
    autosave = request.args.get('autosave', 'true') == 'true'
    persistent_storage = request.args.get('persistent_storage', 'true') == 'true'

    # Figure out options from assignment
    privileged = False
    credentials = False
    network_locked = True
    network_policy = options.get('network_policy', 'os-student')
    resources = options.get('resources', {
        'requests': {"cpu": "250m", "memory": "100Mi"},
        'limits': {"cpu": "2", "memory": "500Mi"},
    })

    # Create a new session
    session = TheiaSession(
        owner_id=current_user.id,
        assignment_id=assignment.id,
        course_id=assignment.course.id,
        image=assignment.theia_image,

        repo_url=repo_url,
        active=True,
        state="Initializing",

        # Options
        network_locked=network_locked,
        network_policy=network_policy,
        privileged=privileged,
        autosave=autosave,
        resources=resources,
        credentials=credentials,
        persistent_storage=persistent_storage,
    )
    db.session.add(session)
    db.session.commit()

    # Send kube resource initialization rpc job
    enqueue_ide_initialize(session.id)

    # Redirect to proxy
    return success_response({
        "active": session.active,
        "session": session.data,
        "status": "Session created",
    })
