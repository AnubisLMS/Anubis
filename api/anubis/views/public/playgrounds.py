from flask import Blueprint, request

from anubis.ide.conditions import assert_theia_sessions_enabled
from anubis.ide.initialize import initialize_ide
from anubis.models import TheiaSession, TheiaImage, TheiaImageTag
from anubis.utils.auth.http import require_user
from anubis.utils.auth.user import current_user
from anubis.utils.http import success_response, req_assert
from anubis.utils.http.decorators import json_response, load_from_id
from anubis.constants import DEVELOPER_DEFAULT_IMAGE, DEVELOPER_DEFAULT_OPTIONS, AUTOGRADE_IDE_DEFAULT_IMAGE

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

    # Assert that the selected image is public
    req_assert(theia_image.public, message="Unable to find", status_code=400)

    # Get the requested tag information
    requested_tag = request.args.get("tag", "latest")
    image_tag_id = None
    if requested_tag != "latest":
        image_tag: TheiaImageTag = TheiaImageTag.query.filter(
            TheiaImageTag.id == requested_tag,
            TheiaImageTag.image_id == theia_image.id,
        ).first()
        if image_tag is not None:
            image_tag_id = image_tag.id

    # Check if there is an active session
    active_session = TheiaSession.query.filter(
        TheiaSession.owner_id == current_user.id,
        TheiaSession.playground == True,
        TheiaSession.active == True,
    ).first()

    # If there was an existing session for this assignment found, skip
    # the initialization, and return the active session information.
    if active_session is not None:
        return success_response({
            "active": active_session.active,
            "session": active_session.data,
        })

    # Assert that new ide starts are allowed. If they are not, then
    # we return a status message to the user saying they are not able
    # to start a new ide.
    assert_theia_sessions_enabled()

    # Default status
    status = "Session created"

    # Default to not setting
    resources = dict()
    docker = False
    autograde = False

    # If the person launching is a developer, then add the extra stuff
    if current_user.is_anubis_developer and theia_image.image == DEVELOPER_DEFAULT_IMAGE:
        status = "Developer session created"
        resources = DEVELOPER_DEFAULT_OPTIONS['resources']
        docker = True

    if theia_image.image == AUTOGRADE_IDE_DEFAULT_IMAGE:
        status = "Autograde session created"
        autograde = True

    # Create IDE
    session: TheiaSession = initialize_ide(
        image_id=theia_image.id,
        image_tag_id=image_tag_id,
        assignment_id=None,
        course_id=None,
        repo_url="",
        playground=True,
        network_locked=True,
        network_policy="os-student",
        persistent_storage=True,
        autosave=False,
        autograde=autograde,
        resources=resources,
        admin=False,
        credentials=False,
        docker=docker,
    )

    # Redirect to proxy
    return success_response(
        {
            "active": session.active,
            "session": session.data,
            "status": status,
        }
    )


@playgrounds_.route("/active")
@require_user()
@json_response
def public_playgrounds_active():
    """
    list all sessions, active and inactive

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
    return success_response(
        {
            "active": True,
            "session": session.data,
        }
    )


@playgrounds_.get("/images")
@require_user()
@json_response
def public_playgrounds_images():
    """
    Get public images

    :return:
    """

    images: list[TheiaImage] = TheiaImage.query.filter(TheiaImage.public == True).all()

    return success_response({
        "images": list(sorted(
            [image.data for image in images],
            key=lambda image_data: image_data['title']
        ))
    })
