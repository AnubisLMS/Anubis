from flask import Blueprint, request

from anubis.models import User, Submission
from anubis.utils.auth import current_user, require_user
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import error_response, success_response, get_number_arg
from anubis.utils.lms.courses import is_course_admin, assert_course_context
from anubis.utils.lms.submissions import regrade_submission, get_submissions

submissions = Blueprint(
    "public-submissions", __name__, url_prefix="/public/submissions"
)


@submissions.route("/")
@require_user()
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

    # Get the limit and offset for submissions query
    limit: int = get_number_arg('limit', default_value=10)
    offset: int = get_number_arg('offset', default_value=0)

    # Load current user
    user: User = current_user()
    perspective_of = user
    if perspective_of_id is not None:
        perspective_of = User.query.filter(User.id == perspective_of_id).first()

    # If the request is from the perspective of a different user,
    # we need to make sure the requester is an admin in the current
    # course context.
    if perspective_of_id is not None and not is_course_admin(course_id):
        return error_response("Bad Request"), 400

    # Get a possibly cached list of submission data
    _submissions, _total = get_submissions(
        user_id=perspective_of_id or user.id,
        course_id=course_id,
        assignment_id=assignment_id,
        limit=limit,
        offset=offset,
    )

    # If the submissions query returned None, something went wrong
    if _submissions is None:
        return error_response("Bad Request"), 400

    # Get submissions through cached function
    return success_response({
        "submissions": _submissions,
        "total": _total,
        "user": perspective_of.data
    })


@submissions.route("/get/<string:commit>")
@require_user()
@json_response
def public_submission(commit: str):
    """
    Get submission data for a given commit.

    :param commit:
    :return:
    """
    # Get current user
    user: User = current_user()

    if not user.is_superuser:
        # Try to find commit (verifying ownership)
        s = Submission.query.filter(
            Submission.owner_id == user.id,
            Submission.commit == commit,
        ).first()

    else:
        # Try to find commit (verifying not ownership)
        s = Submission.query.filter(
            Submission.commit == commit,
        ).first()

    # Make sure we caught one
    if s is None:
        return error_response("Submission does not exist")

    # Hand back submission
    return success_response({"submission": s.full_data})


@submissions.route("/regrade/<string:commit>")
@require_user()
@json_response
def public_regrade_commit(commit: str):
    """
    This route will get hit whenever someone clicks the regrade button on a
    processed assignment. It should do some validity checks on the commit and
    netid, then reset the submission and re-enqueue the submission job.
    """

    # Load current user
    user: User = current_user()

    # Find the submission
    submission: Submission = Submission.query.filter(
        Submission.commit == commit
    ).first()

    # Verify Ownership
    if submission is None:
        return error_response("invalid commit hash")

    # Check that the owner matches the user
    if submission.owner_id != user.id:
        # If the user is not the owner, then full stop if
        assert_course_context(submission)

    # Check that autograde is enabled for the assignment
    if not submission.assignment.autograde_enabled:
        return error_response('Autograde is disabled for this assignment')

    # Check that the submission is allowed to be accepted
    if not submission.accepted:
        return error_response('Submission was rejected for being late')

    # Regrade
    return regrade_submission(submission)
