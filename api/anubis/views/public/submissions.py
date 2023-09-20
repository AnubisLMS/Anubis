from flask import Blueprint, request

from anubis.lms.courses import assert_course_context, is_course_admin
from anubis.lms.submissions import get_submissions, regrade_submission
from anubis.models import Submission, User
from anubis.utils.auth.http import require_user
from anubis.utils.auth.user import current_user
from anubis.utils.data import req_assert
from anubis.utils.http import get_number_arg, success_response
from anubis.utils.http.decorators import json_response

submissions_ = Blueprint("public-submissions", __name__, url_prefix="/public/submissions")


@submissions_.route("/")
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
    limit: int = get_number_arg("limit", default_value=5)
    offset: int = get_number_arg("offset", default_value=0)

    # Load current user
    perspective_of = current_user
    if perspective_of_id is not None:
        perspective_of = User.query.filter(User.id == perspective_of_id).first()

    # If the request is from the perspective of a different user,
    # we need to make sure the requester is an admin in the current
    # course context.
    req_assert(
        not (perspective_of_id is not None and not is_course_admin(course_id)),
        message="Bad Request",
        status_code=400,
    )

    # Get a possibly cached list of submission data
    submissions, total = get_submissions(
        user_id=perspective_of_id or current_user.id,
        course_id=course_id,
        assignment_id=assignment_id,
        limit=limit,
        offset=offset,
    )

    # If the submissions query returned None, something went wrong
    req_assert(submissions is not None, message="Bad Request", status_code=400)

    # Get submissions through cached function
    return success_response({"submissions": submissions, "total": total, "user": perspective_of.data})


@submissions_.route("/get/<string:submission_id>")
@require_user()
@json_response
def public_submission(submission_id: str):
    """
    Get submission data for a given commit.

    :param commit:
    :return:
    """

    # Build submission query
    query = Submission.query.filter(Submission.id == submission_id)

    # Do query
    submission: Submission = query.first()

    # Make sure we caught one
    req_assert(submission is not None, message="submission does not exist")

    # Course that the submission belongs to
    course_id = submission.assignment.course_id

    # Make sure the user is allowed to see the submission if it does not belong to them
    if not submission.owner_id == current_user.id:
        # Assert that the current user is a admin for the course (TA, Professor, Superuser).
        # If they are not, then pass back that submissions does not exist message.
        req_assert(
            is_course_admin(course_id, current_user.id),
            message="submission does not exist",
        )

    # If they are a course admin, give full admin data
    if is_course_admin(course_id):
        return success_response({"submission": submission.admin_data})

    # Hand back submission
    return success_response({"submission": submission.full_data})


@submissions_.route("/regrade/<string:commit>")
@require_user()
@json_response
def public_regrade_commit(commit: str):
    """
    This route will get hit whenever someone clicks the regrade button on a
    processed assignment. It should do some validity checks on the commit and
    netid, then reset the submission and re-enqueue the submission job.
    """

    # Build submission query
    query = Submission.query.filter(Submission.commit == commit)

    # If the current user is not a superuser, then add a filter
    # to make sure the submission is owned by the current user.
    if not current_user.is_superuser:
        query = query.filter(Submission.owner_id == current_user.id)

    # Do query
    submission = query.first()

    # Verify Ownership
    req_assert(submission is not None, message="submission does not exist")

    # Check that the owner matches the user
    if submission.owner_id != current_user.id:
        # If the user is not the owner, then full stop if
        assert_course_context(submission)

    # Check that autograde is enabled for the assignment
    req_assert(
        submission.assignment.autograde_enabled,
        message="Autograde is disabled for this assignment",
    )

    # Check that the submission is allowed to be accepted
    req_assert(submission.accepted, message="Submission was rejected for being late")

    # Regrade
    return regrade_submission(submission)
