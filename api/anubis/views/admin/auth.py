import json

from flask import Blueprint, Response

from anubis.models import User
from anubis.utils.auth.http import require_superuser
from anubis.utils.auth.token import create_token
from anubis.utils.data import is_debug, req_assert
from anubis.utils.http import success_response

auth = Blueprint("admin-auth", __name__, url_prefix="/admin/auth")


@auth.route("/token/<netid>")
@require_superuser(unless_debug=True)
def private_token_netid(netid):
    """
    For debugging, you can use this to sign in as the given user.

    :param netid:
    :return:
    """

    # Get other user
    other = User.query.filter_by(netid=netid).first()

    # Verify that the other user exists
    req_assert(other is not None, message='user does not exist')

    # Verify that the other user is not a superuser
    if not is_debug():
        req_assert(not other.is_superuser, message='You cannot log in as a superuser')

    token = create_token(other.netid)
    res = Response(
        json.dumps(success_response(token)),
        headers={"Content-Type": "application/json"},
    )
    res.set_cookie("token", token, httponly=True)

    return res
