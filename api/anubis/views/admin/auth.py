import json

from flask import Blueprint, Response

from anubis.models import User
from anubis.utils.users.auth import create_token, require_admin
from anubis.utils.http.data import is_debug
from anubis.utils.http.https import error_response, success_response

auth = Blueprint("admin-auth", __name__, url_prefix="/admin/auth")


@auth.route("/token/<netid>")
@require_admin(unless_debug=True)
def private_token_netid(netid):
    """
    For debugging, you can use this to sign in as the given user.

    :param netid:
    :return:
    """
    other = User.query.filter_by(netid=netid).first()
    if other is None:
        return error_response("User does not exist")

    if not is_debug() and other.is_superuser:
        return error_response("You can not log in as a superuser.")

    token = create_token(other.netid)
    res = Response(
        json.dumps(success_response(token)),
        headers={"Content-Type": "application/json"},
    )
    res.set_cookie("token", token, httponly=True)

    return res
