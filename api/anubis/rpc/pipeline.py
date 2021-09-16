from kubernetes import config, client

from anubis.models import db, Config, Submission
from anubis.utils.data import with_context
from anubis.utils.k8s.pipeline import create_pipeline_job_obj, reap_pipeline_jobs
from anubis.utils.logging import logger


@with_context
def create_submission_pipeline(submission_id: str):
    """
    This function should launch the appropriate testing container
    for the assignment, passing along the function arguments.

    :param submission_id: submission.id of to test
    """
    from anubis.utils.rpc import enqueue_autograde_pipeline
    from anubis.lms.submissions import init_submission

    # Log the creation event
    logger.info(
        "Creating submission pipeline job {}".format(submission_id),
        extra={
            "submission_id": submission_id,
        },
    )

    # Calculate the maximum number of jobs allowed in the cluster
    max_jobs = Config.query.filter(Config.key == "MAX_JOBS").first()
    max_jobs = int(max_jobs.value) if max_jobs is not None else 10

    # Initialize kube client
    config.load_incluster_config()

    # Cleanup finished jobs
    active_jobs = reap_pipeline_jobs()

    if active_jobs > max_jobs:
        logger.info(
            "TOO many jobs - re-enqueue {}".format(submission_id),
            extra={"submission_id": submission_id},
        )
        enqueue_autograde_pipeline(submission_id)
        exit(0)

    # Get the database entry for the submission
    submission = Submission.query.filter(
        Submission.id == submission_id
    ).first()

    # Make sure that the submission exists
    if submission is None:
        logger.error(
            "Unable to find submission rpc.test_repo",
            extra={
                "submission_id": submission_id,
            },
        )
        return

    # If the build field is not present, then
    # we need to initialize the submission.
    if submission.build is None:
        init_submission(submission, commit=True)

    submission.processed = False
    submission.state = 'Initializing Pipeline'
    db.session.commit()

    # Create k8s job object
    job = create_pipeline_job_obj(submission)

    # Log the pipeline job creation
    logger.debug("creating pipeline job: " + job.to_str())

    # Send to kube api
    batch_v1 = client.BatchV1Api()
    batch_v1.create_namespaced_job(body=job, namespace="anubis")
