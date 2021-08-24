from flask import Blueprint

from anubis.utils.auth.http import require_superuser
from anubis.utils.data import is_debug, req_assert
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import success_response
from anubis.utils.services.rpc import enqueue_seed

seed = Blueprint("admin-seed", __name__, url_prefix="/admin/seed")


@seed.route("")
@seed.route("/")
@require_superuser(unless_debug=True)
@json_response
def admin_seed():
    """
    Seed debug data.

    :return:
    """

    # Only allow seed to run if in debug mode
    req_assert(is_debug(), message='seed only enabled in debug mode')

    # Enqueue a seed job
    enqueue_seed()

    # Return the status
    return success_response({
        'status': 'enqueued seed'
    })
