from datetime import datetime, timedelta

from anubis.lms.courses import get_course_users
from anubis.models import Submission, Assignment
from anubis.utils.data import with_context, split_chunks

# Regrade all assignment based of a student with a user id
@with_context
def bulk_regrade_assignment_of_student(
    user_id: str,
    hours: int = -1,
    not_processed: int = -1,
    processed: int = -1,
    reaped: int = -1,
    latest_only: int = -1,
):
    # Check if the user is a student
    
    # Fetch all submisions of a user
    from anubis.lms.submissions import get_latest_user_submissions_by_user

    # Build a list of filters based on the options
    filters = []
    if latest_only <= 1:

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

    submissions = get_latest_user_submissions_by_user(user_id, filter=filters)
    
    # Split the submissions into bite sized chunks
    submission_ids = [s.id for s in submissions]
    submission_chunks = split_chunks(submission_ids, 100)

    from anubis.rpc.enqueue import enqueue_bulk_regrade_submissions

    # Enqueue each chunk as a job for the rpc workers
    for chunk in submission_chunks:
        enqueue_bulk_regrade_submissions(chunk)


@with_context
def bulk_regrade_assignment(
    assignment_id: str,
    hours: int = -1,
    not_processed: int = -1,
    processed: int = -1,
    reaped: int = -1,
    latest_only: int = -1,
):
    from anubis.lms.submissions import get_latest_user_submissions

    assignment: Assignment = Assignment.query.filter(
        Assignment.id == assignment_id,
    ).first()

    if latest_only > 1:
        users = get_course_users(assignment)
        submissions = []
        for user in users:
            submissions.extend(get_latest_user_submissions(assignment, user))

    else:
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

        # Get all submissions matching the filters
        submissions = Submission.query.filter(
            Submission.assignment_id == assignment_id,
            Submission.owner_id is not None,
            *filters,
        ).all()

    # Split the submissions into bite sized chunks
    submission_ids = [s.id for s in submissions]
    submission_chunks = split_chunks(submission_ids, 100)

    from anubis.rpc.enqueue import enqueue_bulk_regrade_submissions

    # Enqueue each chunk as a job for the rpc workers
    for chunk in submission_chunks:
        enqueue_bulk_regrade_submissions(chunk)
