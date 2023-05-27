from datetime import datetime, timedelta

from anubis.lms.courses import get_course_users
from anubis.models import User, Submission, Assignment
from anubis.utils.data import with_context, split_chunks
from anubis.lms.submissions import get_latest_user_submissions
from anubis.lms.assignments import get_assignment_due_date


def chunk_and_enqueue_regrade(submissions: list[Submission]):
    # Split the submissions into bite sized chunks
    submission_ids = [s.id for s in submissions]
    submission_chunks = split_chunks(submission_ids, 100)

    from anubis.rpc.enqueue import enqueue_bulk_regrade_submissions
    # Enqueue each chunk as a job for the rpc workers
    for chunk in submission_chunks:
        enqueue_bulk_regrade_submissions(chunk)


def regrade_filters(
    hours: int = -1,
    not_processed: int = -1,
    processed: int = -1,
    reaped: int = -1,
) -> list:
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
        filters.append(Submission.state == "Reaped after timeout")

    return filters


@with_context
def bulk_regrade_assignment_of_student(
    user_id: str,
    hours: int = -1,
    not_processed: int = -1,
    processed: int = -1,
    reaped: int = -1,
    latest_only: int = -1,
):
    # Build a list of filters based on the options
    filters = regrade_filters(hours, not_processed, processed, reaped)

    # Grab actual user
    user: User = User.query.filter(User.id == user_id).first()

    # Proceed to only filter submissions that are not past the assignment due date (including grace date)
    submissions = get_latest_user_submissions(user=user, limit=100, filter=filters)
    submissions = [s for s in submissions if s.created < get_assignment_due_date(user_id, s.assignment_id, True)]

    if latest_only > 0:
        # If only latest, just grab the front submission
        submissions = submissions[0] if len(submissions) > 0 else []

    chunk_and_enqueue_regrade(submissions)


@with_context
def bulk_regrade_assignment(
    assignment_id: str,
    hours: int = -1,
    not_processed: int = -1,
    processed: int = -1,
    reaped: int = -1,
    latest_only: int = -1,
):
    assignment: Assignment = Assignment.query.filter(
        Assignment.id == assignment_id,
    ).first()

    if latest_only > 0:
        submissions = []
        users = get_course_users(assignment)
        for user in users:
            submissions.extend(get_latest_user_submissions(assignment, user, limit=1))

    else:
        # Build a list of filters based on the options
        filters = regrade_filters(hours, not_processed, processed, reaped)

        # Get all submissions matching the filters
        submissions = Submission.query.filter(
            Submission.assignment_id == assignment_id,
            Submission.owner_id is not None,
            *filters,
        ).all()

    chunk_and_enqueue_regrade(submissions)
