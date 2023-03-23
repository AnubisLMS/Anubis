from datetime import datetime, timedelta

from flask import Blueprint, request

from anubis.ide.conditions import assert_theia_sessions_enabled
from anubis.ide.get import get_n_available_sessions
from anubis.ide.initialize import initialize_ide_for_assignment
from anubis.ide.poll import theia_poll_ide
from anubis.ide.redirect import theia_redirect_url
from anubis.lms.assignments import get_assignment_due_date
from anubis.lms.courses import is_course_admin
from anubis.models import Assignment, TheiaSession, db
from anubis.rpc.enqueue import enqueue_ide_stop
from anubis.utils.auth.http import require_user
from anubis.utils.auth.user import current_user
from anubis.utils.cache import cache
from anubis.utils.data import req_assert
from anubis.utils.http import error_response, success_response
from anubis.utils.http.decorators import json_response, load_from_id

ide_ = Blueprint("public-ide", __name__, url_prefix="/public/ide")


@ide_.post("/initialize/<string:id>")
@require_user()
@load_from_id(Assignment, verify_owner=False)
@json_response
def public_ide_initialize(assignment: Assignment):
    """
    Redirect to theia proxy.

    :param assignment:
    :return:
    """

    # verify that ides are enabled for this assignment
    req_assert(assignment.ide_enabled, message="IDEs are not enabled for this assignment")

    # Check for existing active session
    active_session = (
        TheiaSession.query.join(Assignment)
        .filter(
            TheiaSession.owner_id == current_user.id,
            TheiaSession.assignment_id == assignment.id,
            TheiaSession.active,
        )
        .first()
    )

    # If there was an existing session for this assignment found, skip
    # the initialization, and return the active session information.
    if active_session is not None:
        return success_response({"active": active_session.active, "session": active_session.data})

    # Assert that new ide starts are allowed. If they are not, then
    # we return a status message to the user saying they are not able
    # to start a new ide.
    assert_theia_sessions_enabled()

    # If the user requesting this IDE is a course admin (ta/professor/superuser), then there
    # are a few places we handle things differently.
    is_admin = is_course_admin(assignment.course_id)

    # If it is a student (not a ta) requesting the ide, then we will need to
    # make sure that the assignment has actually been released.
    if not is_admin:

        # If the assignment has been released, then we cannot allocate a session to a student
        req_assert(
            assignment.release_date < datetime.now(),
            message="Assignment has not been released",
        )

        # Get due date for this assignment. There may be a LateException on record for this student.
        # In that case, this function will pull the proper datetime.
        due_date = get_assignment_due_date(current_user.id, assignment.id, grace=True)

        # If 3 weeks has passed since the assignment has been due, then we should not allow
        # new sessions to be created
        if due_date + timedelta(days=3 * 7) <= datetime.now():
            return error_response("Assignment due date passed over 3 weeks ago. IDEs are disabled.")

    user_options = dict()
    if request.is_json:
        user_options = dict(**request.json)
        print(f"{request.json=}")

    # Initialize IDE for assignment
    session = initialize_ide_for_assignment(
        current_user,
        assignment,
        user_options=user_options,
    )

    return success_response({
        "active":  session.active,
        "session": session.data,
        "status":  "Session created",
    })


@ide_.route("/available")
@require_user()
@json_response
def public_ide_available():
    """
    list all sessions, active and inactive

    :return:
    """

    # Get the active and maximum number of ides currently allocated
    active_count, max_count = get_n_available_sessions()

    # Calculate if sessions are available
    session_available: bool = active_count < max_count

    # pass back if sessions are available
    return success_response(
        {
            "session_available": session_available,
        }
    )


@ide_.route("/active/<string:assignment_id>")
@require_user()
@json_response
def public_ide_active(assignment_id):
    """
    list all sessions, active and inactive

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
    return success_response(
        {
            "active":  True,
            "session": session.data,
        }
    )


@ide_.route("/stop/<string:theia_session_id>")
@require_user()
def public_ide_stop(theia_session_id: str) -> dict[str, str]:
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
    req_assert(theia_session is not None, message="session does not exist")

    # Mark the session as stopped.
    theia_session.active = False
    theia_session.ended = datetime.now()
    theia_session.state = "Ended"

    # Commit the change
    db.session.commit()

    # Enqueue a ide stop job
    enqueue_ide_stop(theia_session.id)

    # Clear poll cache
    # cache.delete_memoized(theia_poll_ide, theia_session_id, current_user.id)

    # Pass back the status
    return success_response(
        {
            "status":  "Session stopped.",
            "variant": "warning",
        }
    )


@ide_.route("/poll/<string:theia_session_id>")
@require_user()
@json_response
def public_ide_poll(theia_session_id: str) -> dict[str, str]:
    """
    Slightly cached endpoint for polling for session data.

    :param theia_session_id:
    :return:
    """

    # Find the (possibly cached) session data
    session_data = theia_poll_ide(theia_session_id, current_user.id)

    # Assert that the session exists
    req_assert(session_data is not None, message="session does not exist")

    # Check to see if it is still initializing
    session_state = session_data["state"]
    loading = session_state not in {"Running", "Ended", "Failed"}

    # Map of session state code to the status message that should
    # be displayed on the frontend.
    status, variant = {
        "Running": ("Session is now ready.", "success"),
        # "Ended": ("Session ended.", "warning"),
        "Failed":  ("Session failed to start. Please try again.", "error"),
    }.get(session_state, (None, None))

    # Pass back the status and data
    return success_response(
        {
            "loading": loading,
            "session": session_data,
            "status":  status,
            "variant": variant,
        }
    )


@ide_.route("/redirect-url/<string:theia_session_id>")
@require_user()
@json_response
def public_ide_redirect_url(theia_session_id: str) -> dict[str, str]:
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
    req_assert(theia_session is not None, message="session does not exist")

    # Pass back redirect link
    return success_response({"redirect": theia_redirect_url(theia_session.id, current_user.netid)})
