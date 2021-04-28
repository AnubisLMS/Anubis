from flask import Blueprint

from anubis.utils.auth import require_admin
from anubis.utils.data import is_debug
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import success_response, error_response
from anubis.utils.services.rpc import enqueue_seed as seed_

seed = Blueprint("admin-seed", __name__, url_prefix="/admin/seed")


@seed.route("/")
@require_admin(unless_debug=True)
@json_response
def private_seed():
    if not is_debug():
        return error_response('Seed only enabled in debug mode')

    seed_()
    return success_response({
        'status': 'enqueued seed'
    })
