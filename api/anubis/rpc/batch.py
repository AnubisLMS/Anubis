from anubis.utils.logger import get_logger


def rpc_bulk_regrade(submissions):
    from anubis.app import create_app
    from anubis.utils.submissions import bulk_regrade_submission

    app = create_app()
    logger = get_logger()

    logger.info(
        "bulk regrading {}".format(submissions),
        extra={
            "submission_id": submissions,
        },
    )

    with app.app_context():
        bulk_regrade_submission(submissions)
