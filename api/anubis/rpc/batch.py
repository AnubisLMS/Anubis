from anubis.utils.data import with_context
from anubis.utils.logging import logger


@with_context
def rpc_bulk_regrade(submissions):
    from anubis.lms.submissions import bulk_regrade_submissions

    logger.info(
        "bulk regrading {}".format(submissions),
        extra={
            "submission_id": submissions,
        },
    )

    bulk_regrade_submissions(submissions)
