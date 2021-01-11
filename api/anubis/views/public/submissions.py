from flask import Blueprint, request

from anubis.models import User, Submission

from anubis.utils.assignments import get_submissions
from anubis.utils.auth import current_user, require_user
from anubis.utils.cache import cache
from anubis.utils.data import is_debug
from anubis.utils.decorators import json_response
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import error_response, success_response
from anubis.utils.submissions import regrade_submission
from anubis.utils.logger import logger

submissions = Blueprint(
    "public-submissions", __name__, url_prefix="/public/submissions"
)


@submissions.route("/")
@require_user
@log_endpoint("public-submissions")
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
    course_id = request.args.get("courseId", default=None)
    perspective_of_id = request.args.get("userId", default=None)
    assignment_id = request.args.get("assignmentId", default=None)

    # Load current user
    user: User = current_user()

    if perspective_of_id is not None and not (user.is_admin or user.is_superuser):
        return error_response('Bad Request'), 400

    logger.debug('id: ' + str(perspective_of_id))
    logger.debug('id: ' + str(perspective_of_id or user.id))

    submissions_ = get_submissions(
        user_id=perspective_of_id or user.id,
        course_id=course_id,
        assignment_id=assignment_id,
    )

    if submissions_ is None:
        return error_response('Bad Request'), 400

    # Get submissions through cached function
    return success_response(
        {
            "submissions": submissions_
        }
    )


@submissions.route("/get/<string:commit>")
@require_user
@log_endpoint(
    "public-submission-commit", lambda: "get submission {}".format(request.path)
)
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
    s = Submission.query.filter(
        Submission.owner_id == user.id, Submission.commit == commit
    ).first()

    # Make sure we caught one
    if s is None:
        return error_response("Commit does not exist"), 406

    # Hand back submission
    return success_response({"submission": s.full_data})


@submissions.route("/regrade/<commit>")
@require_user
@log_endpoint("regrade-request", lambda: "submission regrade request " + request.path)
@json_response
def public_regrade_commit(commit=None):
    """
    This route will get hit whenever someone clicks the regrade button on a
    processed assignment. It should do some validity checks on the commit and
    netid, then reset the submission and re-enqueue the submission job.
    """
    if commit is None:
        return error_response("incomplete_request"), 406

    # Load current user
    user: User = current_user()

    # Find the submission
    submission: Submission = (
        Submission.query.join(User)
            .filter(Submission.commit == commit, User.netid == user.netid)
            .first()
    )

    # Verify Ownership
    if submission is None:
        return error_response("invalid commit hash or netid"), 406

    # Regrade
    return regrade_submission(submission)
