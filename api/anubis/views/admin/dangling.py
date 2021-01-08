from flask import Blueprint

from anubis.models import Submission
from anubis.utils.decorators import json_response
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import success_response
from anubis.utils.submissions import fix_dangling

dangling = Blueprint('admin-dangling', __name__, url_prefix='/admin/dangling')


@dangling.route('/')
@log_endpoint('cli', lambda: 'dangling')
@json_response
def private_dangling():
    """
    This route should hand back a json list of all submissions that are dangling.
    Dangling being that we have no netid to match to the github username that
    submitted the assignment.
    """

    dangling_ = Submission.query.filter(
        Submission.owner_id == None,
    ).all()
    dangling_ = [a.data for a in dangling_]

    return success_response({
        "dangling": dangling_,
        "count": len(dangling_)
    })


@dangling.route('/reset')
@log_endpoint('reset-dangling', lambda: 'reset-dangling')
@json_response
def private_reset_dangling():
    resets = []
    for s in Submission.query.filter_by(owner_id=None).all():
        s.init_submission_models()
        resets.append(s.data)
    return success_response({'reset': resets})


@dangling.route('/fix')
@log_endpoint('cli', lambda: 'fix-dangling')
@json_response
def private_fix_dangling():
    """
    Attempt to fix dangling. A dangling submission is one we can't match
    to a user. We can only see the github username when someone pushes.
    If we cant match that username to a user at that time, we create a
    dangling submission. That is a submission that has no owner. We create
    a submission in the database, but do not process it. Once we have
    the student github username, we'll need to check to see if
    we can find dangling submissions by them. That situation is what
    this endpoint is for.

    We go through all the existing dangling submissions and attempt to
    find a user for which the github username matches.

    :return:
    """
    return fix_dangling()
