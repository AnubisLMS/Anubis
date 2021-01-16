from flask import Blueprint

from anubis.rpc.theia import reap_all_theia_sessions
from anubis.utils.decorators import json_response
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import success_response
from anubis.utils.redis_queue import rpc_enqueue
from anubis.utils.auth import require_admin

ide = Blueprint("admin-ide", __name__, url_prefix="/admin/ide")


@ide.route("/ide/clear")
@require_admin()
@log_endpoint("cli", lambda: "clear-ide")
@json_response
def private_ide_clear():
    """
    Enqueue a job for the rpc workers to reap all the active
    theia submissions. They will end all active sessions in the
    database, then schedule all the kube resources for deletion.

    :return:
    """
    rpc_enqueue(reap_all_theia_sessions, tuple())

    return success_response({"state": "enqueued"})
