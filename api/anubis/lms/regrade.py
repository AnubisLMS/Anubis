from datetime import datetime, timedelta

from anubis.models import Submission
from anubis.utils.data import with_context, split_chunks
from anubis.utils.logging import logger


@with_context
def bulk_regrade_submissions(submissions):
    from anubis.lms.submissions import bulk_regrade_submissions

    logger.info(
        "bulk regrading {}".format(submissions),
        extra={
            "submission_id": submissions,
        },
    )

    bulk_regrade_submissions(submissions)


@with_context
def bulk_regrade_assignment(
    assignment_id: str,
    hours: int = -1,
    not_processed: int = -1,
    processed: int = -1,
    reaped: int = -1
):
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
