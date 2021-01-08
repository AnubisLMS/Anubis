import json

from flask import Blueprint, Response

from anubis.models import User
from anubis.utils.auth import create_token
from anubis.utils.http import error_response, success_response

auth = Blueprint('admin-auth', __name__, url_prefix='/admin/auth')


@auth.route('/token/<netid>')
def private_token_netid(netid):
    """
    For debugging, you can use this to sign in as the given user.

    :param netid:
    :return:
    """
    user = User.query.filter_by(netid=netid).first()
    if user is None:
        return error_response('User does not exist')
    token = create_token(user.netid)
    res = Response(json.dumps(success_response(token)), headers={'Content-Type': 'application/json'})
    res.set_cookie('token', token, httponly=True)
    return res
