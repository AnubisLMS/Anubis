import math
from datetime import datetime, timedelta

from flask import Blueprint
from sqlalchemy import or_

from anubis.models import Submission, Assignment
from anubis.rpc.batch import rpc_bulk_regrade
from anubis.utils.auth import require_admin
from anubis.utils.data import split_chunks
from anubis.utils.http.decorators import json_response
from anubis.utils.http.decorators import load_from_id
from anubis.utils.http.https import error_response, success_response, get_number_arg
from anubis.utils.lms.course import assert_course_admin, get_course_context, assert_course_context
from anubis.utils.services.elastic import log_endpoint
from anubis.utils.services.rpc import enqueue_autograde_pipeline, rpc_enqueue

regrade = Blueprint("admin-regrade", __name__, url_prefix="/admin/regrade")


@regrade.route("/status/<string:id>")
@require_admin()
@load_from_id(Assignment, verify_owner=False)
@json_response
def admin_regrade_status(assignment: Assignment):
    """
    Get the autograde status for an assignment. The status
    is some high level stats the proportion of submissions
    within the assignment that have been processed

    :param assignment:
    :return:
    """

    # Get the current course context
    course = get_course_context()

    # Assert that the current user is an admin for the course
    assert_course_admin(assignment.course_id)

    # Assert that the assignment is within the current course context
    assert_course_context(assignment.course_id == course.id)

    # Get the number of submissions that are being processed
    processing = Submission.query.filter(
        Submission.assignment_id == assignment.id,
        Submission.processed == False,
    ).count()

    # Get the total number of submissions
    total = Submission.query.filter(
        Submission.assignment_id == assignment.id,
    ).count()

    # Calculate the percent of submissions that have been processed
    percent = math.ceil(((total - processing) / total) * 100) if total > 0 else 0

    # Return the status
    return success_response({
        'percent': f'{percent}% of submissions processed',
        'processing': processing,
        'processed': total - processing,
        'total': total,
    })


@regrade.route("/submission/<string:commit>")
@require_admin()
@log_endpoint("cli", lambda: "regrade-commit")
@json_response
def admin_regrade_submission_commit(commit):
    """
    Regrade a specific submission via the unique commit hash.

    :param commit:
    :return:
    """

    # Get the current course context
    course = get_course_context()

    # Find the submission
    submission: Submission = Submission.query.filter(
        Submission.commit == commit,
        Submission.owner_id is not None,
    ).first()

    # Make sure the submission exists
    if submission is None:
        return error_response("Submission does not exist")

    # Assert that the current user is an admin for the assignment course
    assert_course_admin(submission.assignment.course.id)

    # Assert that the submission is within the current course context
    assert_course_context(submission.assignment.course.id == course.id)

    # Reset submission in database
    submission.init_submission_models()

    # Enqueue the submission pipeline
    enqueue_autograde_pipeline(submission.id)

    # Return status
    return success_response({"submission": submission.data, "user": submission.owner.data})


@regrade.route("/assignment/<string:assignment_id>")
@require_admin()
@log_endpoint("cli", lambda: "regrade")
@json_response
def private_regrade_assignment(assignment_id):
    """
    This route is used to restart / re-enqueue jobs.

    The work required for this is potentially very IO entinsive
    on the database. We basically need to load the entire submission
    history out of the database, reset each, then re-enqueue them
    for processing. This makes resetting a single assignment actually
    very time consuming. For this we need to be a bit smart about how to
    handle this.

    We will split all submissions for the given assignment into
    chunks of 100. We can then push each of those chunks as a
    bulk_regrade job to the rpc workers.

    This solution isn't the fastest, but it gets the job done.

    :param assignment_id: name of assignment to regrade
    :return:
    """

    # Get the current course context
    course = get_course_context()

    # Get the options for the regrade
    hours = get_number_arg('hours', default_value=-1)
    not_processed = get_number_arg('not_processed', default_value=-1)
    processed = get_number_arg('processed', default_value=-1)
    reaped = get_number_arg('reaped', default_value=-1)

    # Build a list of filters based on the options
    filters = []

    # Number of hours back to regrade
    if hours > 0:
        filters.append(Submission.created > datetime.now() - timedelta(hours=hours))

    # Only regrade submissions that have been processed
    if processed == 1:
        filters.append(Submission.processed == True)

    # Only regrade submissions that have not been processed
    if not_processed == 1:
        filters.append(Submission.processed == False)

    # Only regrade submissions that have been reaped
    if reaped == 1:
        filters.append(Submission.state == 'Reaped after timeout')

    # Find the assignment
    assignment = Assignment.query.filter(
        or_(Assignment.id == assignment_id, Assignment.name == assignment_id)
    ).first()

    # Verify that the assignment exists
    if assignment is None:
        return error_response("cant find assignment")

    # Assert that the current user is an admin for the course
    assert_course_admin(assignment.course_id)

    # Assert that the assignment is within the current course context
    assert_course_context(assignment.course_id == course.id)

    # Get all submissions matching the filters
    submissions = Submission.query.filter(
        Submission.assignment_id == assignment.id,
        Submission.owner_id is not None,
        *filters
    ).all()

    # Get a count of submissions for the response
    submission_count = len(submissions)

    # Split the submissions into bite sized chunks
    submission_ids = [s.id for s in submissions]
    submission_chunks = split_chunks(submission_ids, 100)

    # Enqueue each chunk as a job for the rpc workers
    for chunk in submission_chunks:
        rpc_enqueue(rpc_bulk_regrade, 'regrade', args=[chunk])

    # Pass back the enqueued status
    return success_response({
        "status": f"{submission_count} submissions enqueued.",
        "submissions": submission_ids,
    })
