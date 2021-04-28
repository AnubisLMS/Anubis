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
from anubis.utils.lms.course import assert_course_admin
from anubis.utils.services.elastic import log_endpoint
from anubis.utils.services.rpc import enqueue_autograde_pipeline, rpc_enqueue

regrade = Blueprint("admin-regrade", __name__, url_prefix="/admin/regrade")


@regrade.route("/status/<string:id>")
@require_admin()
@load_from_id(Assignment, verify_owner=False)
@json_response
def admin_regrade_status(assignment: Assignment):
    assert_course_admin(assignment.course_id)

    processing = Submission.query.filter(
        Submission.assignment_id == assignment.id,
        Submission.processed == False,
    ).count()

    total = Submission.query.filter(
        Submission.assignment_id == assignment.id,
    ).count()

    percent = 0
    if total > 0:
        percent = math.ceil(((total - processing) / total) * 100)

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
def private_regrade_submission(commit):
    """
    Regrade a specific submission via the unique commit hash.

    :param commit:
    :return:
    """

    # Find the submission
    s: Submission = Submission.query.filter(
        Submission.commit == commit,
        Submission.owner_id is not None,
    ).first()
    if s is None:
        return error_response("not found")

    assert_course_admin(s.assignment.course.id)

    # Reset submission in database
    s.init_submission_models()

    # Enqueue the submission pipeline
    enqueue_autograde_pipeline(s.id)

    # Return status
    return success_response({"submission": s.data, "user": s.owner.data})


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

    extra = []
    hours = get_number_arg('hours', default_value=-1)
    not_processed = get_number_arg('not_processed', default_value=-1)
    processed = get_number_arg('processed', default_value=-1)
    reaped = get_number_arg('reaped', default_value=-1)

    # Add hours to filter query
    if hours > 0:
        extra.append(
            Submission.created > datetime.now() - timedelta(hours=hours)
        )
    if processed == 1:
        extra.append(
            Submission.processed == True,
        )
    if not_processed == 1:
        extra.append(
            Submission.processed == False,
        )
    if reaped == 1:
        extra.append(
            Submission.state == 'Reaped after timeout',
        )

    # Find the assignment
    assignment = Assignment.query.filter(
        or_(Assignment.id == assignment_id, Assignment.name == assignment_id)
    ).first()
    if assignment is None:
        return error_response("cant find assignment")

    assert_course_admin(assignment.course_id)

    # Get all submissions that have an owner (not dangling)
    submissions = Submission.query.filter(
        Submission.assignment_id == assignment.id,
        Submission.owner_id is not None,
        *extra
    ).all()
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
