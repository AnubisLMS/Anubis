from typing import List

from flask import Blueprint

from anubis.lms.theia import initialize_ide, assert_theia_sessions_enabled
from anubis.models import TheiaSession, TheiaImage
from anubis.utils.auth.http import require_user
from anubis.utils.auth.user import current_user
from anubis.utils.http import success_response
from anubis.utils.http.decorators import json_response, load_from_id

playgrounds_ = Blueprint("public-playgrounds", __name__, url_prefix="/public/playgrounds")


@playgrounds_.post("/initialize/<string:id>")
@require_user()
@load_from_id(TheiaImage, verify_owner=False)
@json_response
def public_playgrounds_initialize(theia_image: TheiaImage):
    """
    Start a playground ide with selected image

    :param theia_image:
    :return:
    """

    active_session = TheiaSession.query.filter(
        TheiaSession.owner_id == current_user.id,
        TheiaSession.playground == True,
        TheiaSession.active == True,
    ).first()

    # If there was an existing session for this assignment found, skip
    # the initialization, and return the active session information.
    if active_session is not None:
        return success_response({"active": active_session.active, "session": active_session.data})

    # Assert that new ide starts are allowed. If they are not, then
    # we return a status message to the user saying they are not able
    # to start a new ide.
    assert_theia_sessions_enabled()

    # Create IDE
    session: TheiaSession = initialize_ide(
        image_id=theia_image.id,

        assignment_id=None,
        course_id=None,
        repo_url='',
        playground=True,
        network_locked=True,
        network_policy='os-student',
        persistent_storage=True,
        autosave=False,
        resources=dict(),

        admin=False,
        privileged=False,
        credentials=False,
    )

    # Redirect to proxy
    return success_response({
        "active": session.active,
        "session": session.data,
        "status": "Session created",
    })


@playgrounds_.route("/active")
@require_user()
@json_response
def public_playgrounds_active():
    """
    List all sessions, active and inactive

    :return:
    """

    # Find if they have an active session for this assignment
    session = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.owner_id == current_user.id,
        TheiaSession.playground == True,
    ).first()

    # If they do not have an active assignment, then pass back False
    if session is None:
        return success_response({"active": False})

    # If they do have a session, then pass back True
    return success_response({
        "active": True,
        "session": session.data,
    })


@playgrounds_.get('/images')
@require_user()
@json_response
def public_playgrounds_images():
    """
    Get public images

    :return:
    """

    images: List[TheiaImage] = TheiaImage.query.filter(
        TheiaImage.public == True
    ).all()

    return success_response({
        'images': [image.data for image in images]
    })
