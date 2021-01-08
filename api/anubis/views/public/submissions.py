from flask import Blueprint, request

from anubis.models import User, Submission
from anubis.utils.assignments import get_submissions
from anubis.utils.auth import current_user, require_user
from anubis.utils.cache import cache
from anubis.utils.data import is_debug
from anubis.utils.decorators import json_response
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import get_request_ip, error_response, success_response
from anubis.utils.submissions import regrade_submission

submissions = Blueprint('public-submissions', __name__, url_prefix='/public/submissions')


@submissions.route('/')
@require_user
@log_endpoint('public-submissions', lambda: 'get submissions {}'.format(get_request_ip()))
@json_response
def public_submissions():
    """
    Get all submissions for a given student. Optionally specify class,
    and assignment name filters in get query.


    /api/public/submissions
    /api/public/submissions?class=Intro to OS
    /api/public/submissions?assignment=Assignment 1: uniq
    /api/public/submissions?class=Intro to OS&assignment=Assignment 1: uniq

    :return:
    """
    # Get optional filters
    class_name = request.args.get('class', default=None)
    assignment_name = request.args.get('assignment', default=None)
    assignment_id = request.args.get('assignment_id', default=None)

    # Load current user
    user: User = current_user()

    # Get submissions through cached function
    return success_response({
        'submissions': get_submissions(
            user.netid,
            class_name=class_name,
            assignment_name=assignment_name,
            assignment_id=assignment_id
        )
    })


@submissions.route('/<string:commit>')
@require_user
@log_endpoint('public-submission-commit', lambda: 'get submission {}'.format(request.path))
@json_response
@cache.memoize(timeout=1, unless=is_debug)
def public_submission(commit: str):
    """
    Get submission data for a given commit.

    :param commit:
    :return:
    """
    # Get current user
    user: User = current_user()

    # Try to find commit (verifying ownership)
    s = Submission.query.join(User).filter(
        User.netid == user.netid,
        Submission.commit == commit
    ).first()

    # Make sure we caught one
    if s is None:
        return error_response('Commit does not exist'), 406

    # Hand back submission
    return success_response({'submission': s.full_data})


@submissions.route('/regrade/<commit>')
@require_user
@log_endpoint('regrade-request', lambda: 'submission regrade request ' + request.path)
@json_response
def public_regrade_commit(commit=None):
    """
    This route will get hit whenever someone clicks the regrade button on a
    processed assignment. It should do some validity checks on the commit and
    netid, then reset the submission and re-enqueue the submission job.
    """
    if commit is None:
        return error_response('incomplete_request'), 406

    # Load current user
    user: User = current_user()

    # Find the submission
    submission: Submission = Submission.query.join(User).filter(
        Submission.commit == commit,
        User.netid == user.netid
    ).first()

    # Verify Ownership
    if submission is None:
        return error_response('invalid commit hash or netid'), 406

    # Regrade
    return regrade_submission(submission)
