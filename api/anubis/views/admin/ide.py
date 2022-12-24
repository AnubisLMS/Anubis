import json
from datetime import datetime

from flask import Blueprint

from anubis.constants import THEIA_ADMIN_NETWORK_POLICY
from anubis.ide.initialize import initialize_ide
from anubis.k8s.theia.reap import reap_theia_sessions_in_course
from anubis.lms.courses import course_context
from anubis.models import TheiaSession, TheiaImage, db
from anubis.rpc.enqueue import rpc_enqueue, enqueue_ide_stop
from anubis.utils.auth.http import require_admin
from anubis.utils.auth.user import current_user
from anubis.utils.config import get_config_bool
from anubis.utils.data import req_assert
from anubis.utils.http import error_response, success_response
from anubis.utils.http.decorators import json_endpoint, json_response

ide = Blueprint("admin-ide", __name__, url_prefix="/admin/ide")


def default_admin_ide() -> TheiaImage:
    image = TheiaImage.query.filter(
        TheiaImage.image == "registry.digitalocean.com/anubis/theia-admin",
    ).first()

    return image


@ide.route("/settings")
@require_admin()
@json_response
def admin_ide_admin_settings():
    image = default_admin_ide()

    return success_response(
        {
            "settings": {
                "image": image.data,
                "repo_url": course_context.autograde_tests_repo,
                # Options
                "admin": True,
                "docker": True,
                "network_dns_locked": False,
                "network_policy": THEIA_ADMIN_NETWORK_POLICY,
                "resources": '{"limits": {"cpu": "2", "memory": "2Gi"}, "requests": {"cpu": "1", "memory": "500Mi"}}',
                "autosave": True,
                "credentials": True,
                "persistent_storage": False,
            }
        }
    )


@ide.post("/initialize")
@require_admin()
@json_endpoint([("settings", dict)])
def admin_ide_initialize_custom(settings: dict, **_):
    """
    Initialize a new management ide with options.

    :param settings:
    :param _:
    :return:
    """

    # Check to see if there is already a management session
    # allocated for the current user
    session: TheiaSession = TheiaSession.query.filter(
        TheiaSession.active,
        TheiaSession.owner_id == current_user.id,
        TheiaSession.course_id == course_context.id,
        TheiaSession.assignment_id == None,
    ).first()

    # If there is already a session, then stop
    if session is not None:
        return success_response({"session": session.data})

    default_image = default_admin_ide()

    # Read the options out of the posted data
    image = settings.get("image", dict())
    repo_url = settings.get("repo_url", "https://github.com/os3224/anubis-assignment-tests")
    resources_str = settings.get("resources", '{"limits":{"cpu":"4","memory":"4Gi"}}')
    network_dns_locked = settings.get("network_dns_locked", False)
    network_policy = settings.get("network_policy", THEIA_ADMIN_NETWORK_POLICY)
    autosave = settings.get("autosave", True)
    admin = settings.get("admin", True)
    credentials = settings.get("credentials", True)
    docker = settings.get("docker", True)
    persistent_storage = settings.get("persistent_storage", False)

    image_id = image.get("id", None)
    if image_id is not None:
        image: TheiaImage = TheiaImage.query.filter(TheiaImage.id == image_id).first()
    if image is None or image == dict():
        image: TheiaImage = default_image

    # Attempt to load the options_str into a dict object
    try:
        resources = json.loads(resources_str)
    except json.JSONDecodeError:
        return error_response("Can not parse JSON options")

    # Get the config value for if ide starts are allowed.
    theia_starts_enabled = get_config_bool("THEIA_STARTS_ENABLED", default=True)

    # Assert that new ide starts are allowed. If they are not, then
    # we return a status message to the user saying they are not able
    # to start a new ide.
    req_assert(
        theia_starts_enabled,
        message="Starting new IDEs is currently disabled by an Anubis administrator. " "Please try again later.",
    )

    session: TheiaSession = initialize_ide(
        image_id=image.id,
        assignment_id=None,
        course_id=course_context.id,
        repo_url=repo_url,
        # Options
        admin=admin,
        network_dns_locked=network_dns_locked,
        network_policy=network_policy,
        autosave=autosave,
        resources=resources,
        credentials=credentials,
        persistent_storage=persistent_storage,
        docker=docker,
    )

    return success_response(
        {
            "session": session.data,
            "settings": session.settings,
            "status": "Admin IDE Initialized.",
        }
    )


@ide.route("/active")
@require_admin()
@json_response
def admin_ide_active():
    """
    Get the list of all active Theia ides within
    the current course context.

    :return:
    """

    # Query for an active theia session within this course context
    session = TheiaSession.query.filter(
        TheiaSession.active,
        TheiaSession.owner_id == current_user.id,
        TheiaSession.course_id == course_context.id,
        TheiaSession.assignment_id == None,
    ).first()

    # If there was no session, then stop
    if session is None:
        return success_response({"session": None})

    # Return the active session information
    return success_response(
        {
            "session": session.data,
            "settings": session.settings,
        }
    )


@ide.route("/list")
@require_admin()
@json_response
def admin_ide_list():
    """
    list all active ide sessions

    :return:
    """

    # Get all active sessions
    sessions = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.course_id == course_context.id,
    ).all()

    # Hand back response
    return success_response({"sessions": [session.data for session in sessions]})


@ide.route("/stop/<string:id>")
@require_admin()
@json_response
def admin_ide_stop_id(id: str):
    """
    Stop a specific IDE

    :return:
    """

    # Search for the theia session
    session = TheiaSession.query.filter(
        TheiaSession.id == id,
        TheiaSession.course_id == course_context.id,
    ).first()

    # Verify it exists
    req_assert(session is not None, message="session does not exist")

    # set all the things as stopped
    session.active = False
    session.ended = datetime.now()
    session.state = "Ending"

    # Commit the stop
    db.session.commit()

    # Enqueue the theia stop cleanup
    enqueue_ide_stop(session.id)

    # Hand back response
    return success_response({"status": "Session Killed."})


@ide.route("/reap-all")
@require_admin()
@json_response
def private_ide_reap_all():
    """
    Enqueue a job for the rpc workers to reap all the active
    theia submissions. They will end all active sessions in the
    database, then schedule all the kube resources for deletion.

    :return:
    """

    # Send reap job to rpc cluster
    rpc_enqueue(reap_theia_sessions_in_course, "theia", args=(course_context.id,))

    # Hand back status
    return success_response({"status": "Reap job enqueued. Session cleanup will take a minute."})


@ide.get("/images/list")
@require_admin()
@json_response
def admin_ide_images_list():
    images: list[TheiaImage] = TheiaImage.query.all()

    return success_response({"images": [image.data for image in images]})
