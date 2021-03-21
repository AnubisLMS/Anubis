import json
from datetime import datetime

from flask import Blueprint

from anubis.models import db, TheiaSession
from anubis.rpc.theia import reap_all_theia_sessions
from anubis.utils.auth import require_admin, current_user
from anubis.utils.decorators import json_response, json_endpoint
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import success_response, error_response
from anubis.utils.rpc import enqueue_ide_initialize
from anubis.utils.rpc import rpc_enqueue, enqueue_ide_stop

ide = Blueprint("admin-ide", __name__, url_prefix="/admin/ide")


@ide.route("/initialize")
@require_admin()
@log_endpoint("admin-ide-initialize")
@json_response
def admin_ide_initialize():
    user = current_user()

    session = TheiaSession.query.filter(
        TheiaSession.active,
        TheiaSession.owner_id == user.id,
        TheiaSession.assignment_id == None,
    ).first()

    if session is not None:
        return success_response({
            "session": session.data,
            "settings": session.settings,
        })

    # Create a new session
    session = TheiaSession(
        owner_id=user.id,
        assignment_id=None,
        network_locked=False,
        privileged=True,
        image="registry.osiris.services/anubis/theia-admin",
        repo_url="https://github.com/os3224/anubis-assignment-tests.git",
        options={'limits': {'cpu': '4', 'memory': '4Gi'}},
        active=True,
        state="Initializing",
    )
    db.session.add(session)
    db.session.commit()

    # Send kube resource initialization rpc job
    enqueue_ide_initialize(session.id)

    return success_response({
        "session": session.data,
        "settings": session.settings,
        "status": "Admin IDE Initialized."
    })


@ide.route("/initialize-custom", methods=["POST"])
@require_admin()
@log_endpoint("admin-ide-initialize")
@json_endpoint([('settings', dict)])
def admin_ide_initialize_custom(settings: dict, **_):
    """



    :param settings:
    :param _:
    :return:
    """
    user = current_user()

    session = TheiaSession.query.filter(
        TheiaSession.active,
        TheiaSession.owner_id == user.id,
        TheiaSession.assignment_id == None,
    ).first()

    if session is not None:
        return success_response({"session": session.data})

    network_locked = settings.get('network_locked', False)
    privileged = settings.get('privileged', True)
    image = settings.get('image', 'registry.osiris.services/anubis/theia-admin')
    repo_url = settings.get('repo_url', 'https://github.com/os3224/anubis-assignment-tests')
    options_str = settings.get('options', '{"limits": {"cpu": "4", "memory": "4Gi"}}')

    try:
        options = json.loads(options_str)
    except json.JSONDecodeError:
        return error_response('Can not parse JSON options'), 400

    # Create a new session
    session = TheiaSession(
        owner_id=user.id, assignment_id=None,
        network_locked=network_locked, privileged=privileged,
        image=image, repo_url=repo_url, options=options,
        active=True, state="Initializing",
    )
    db.session.add(session)
    db.session.commit()

    # Send kube resource initialization rpc job
    enqueue_ide_initialize(session.id)

    return success_response({
        "session": session.data,
        "settings": session.settings,
        "status": "Admin IDE Initialized."
    })


@ide.route("/active")
@require_admin()
@log_endpoint("admin-ide-active")
@json_response
def admin_ide_active():
    user = current_user()

    session = TheiaSession.query.filter(
        TheiaSession.active,
        TheiaSession.owner_id == user.id,
        TheiaSession.assignment_id == None,
    ).first()

    if session is None:
        return success_response({"session": None})

    return success_response({
        "session": session.data,
        "settings": session.settings,
    })


@ide.route("/list")
@require_admin()
@log_endpoint("ide-list")
@json_response
def admin_ide_list():
    """
    List all active ide sessions

    :return:
    """

    # Get all active sessions
    sessions = TheiaSession.query.filter(TheiaSession.active).all()

    # Hand back response
    return success_response({"sessions": [session.data for session in sessions]})


@ide.route("/stop/<string:id>")
@require_admin()
@log_endpoint("ide-end")
@json_response
def admin_ide_stop_id(id: str):
    """
    List all active ide sessions

    :return:
    """

    session = TheiaSession.query.filter(TheiaSession.id == id).first()

    if session is None:
        return error_response("Session does not exist.")

    session.active = False
    session.ended = datetime.now()
    session.state = "Ending"
    db.session.commit()

    enqueue_ide_stop(session.id)

    # Hand back response
    return success_response({"status": "Session Killed."})


@ide.route("/reap-all")
@require_admin()
@log_endpoint("ide-reap-all")
@json_response
def private_ide_reap_all():
    """
    Enqueue a job for the rpc workers to reap all the active
    theia submissions. They will end all active sessions in the
    database, then schedule all the kube resources for deletion.

    :return:
    """

    # Send reap job to rpc cluster
    rpc_enqueue(reap_all_theia_sessions, tuple())

    # Hand back status
    return success_response(
        {"status": "Reap job enqueued. Session cleanup will take a minute."}
    )
