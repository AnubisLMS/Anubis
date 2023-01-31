import traceback
from datetime import datetime, timedelta

import kubernetes
from kubernetes import client

from anubis.k8s.pipeline.get import get_active_pipeline_jobs
from anubis.models import Submission, db
from anubis.utils.config import get_config_int
from anubis.utils.logging import logger
from anubis.utils.redis import create_redis_lock


def reap_pipeline_job(job: client.V1Job, submission: Submission):
    # Capture the pipeline log
    submission.pipeline_log = _read_pipeline_job_log(job)
    db.session.add(submission)
    db.session.commit()

    # Attempt to delete the k8s job
    delete_pipeline_job(job)


def delete_pipeline_job(job: client.V1Job):
    batch_v1 = client.BatchV1Api()

    # Log that we are cleaning up the job
    logger.info("deleting namespaced job {}".format(job.metadata.name))
    try:
        return batch_v1.delete_namespaced_job(
            job.metadata.name,
            job.metadata.namespace,
            propagation_policy="Background",
        )
    except kubernetes.client.exceptions.ApiException:
        logger.error("failed to delete api job, continuing" + traceback.format_exc())


def _read_pipeline_job_log(job: client.V1Job) -> str:
    v1 = client.CoreV1Api()
    logger.info(f'Reading logs for job: {job.metadata.name}')
    pods = v1.list_namespaced_pod(
        namespace=job.metadata.namespace,
        label_selector=f"job-name={job.metadata.name}"
    )

    pod = None
    for _pod in pods.items:
        if _pod.status.phase == "Succeeded":
            pod = _pod
            break
    else:
        logger.error(f"could not find successful pod for job: {job.metadata.name}")
        return ''

    try:
        return v1.read_namespaced_pod_log(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            container="pipeline",
        )[:(2 ** 16) - 1]  # TODO put max TEXT length in constants.py
    except kubernetes.client.exceptions.ApiException:
        logger.error("failed to get pod logs, continuing" + traceback.format_exc())
        return 'UNABLE TO GET PIPELINE LOG'


def reap_pipeline_jobs():
    """
    Runs through all jobs in the namespace. If the job is finished, it will
    send a request to the kube api to delete it. Number of active jobs is
    returned.

    :return: number of active jobs
    """

    # Get all pipeline jobs in the anubis namespace
    jobs = get_active_pipeline_jobs()

    # Get the autograde pipeline timeout from config
    autograde_pipeline_timeout_minutes = get_config_int("AUTOGRADE_PIPELINE_TIMEOUT_MINUTES", default=5)

    # Iterate through all pipeline jobs
    for job in jobs:
        job: client.V1Job

        # If submission id not in labels just skip. Job ttl will delete itself.
        if 'submission-id' not in job.metadata.labels:
            logger.error(f'skipping job based off old label format: {job.metadata.name}')
            continue

        # Read submission id from labels
        submission_id = job.metadata.labels['submission-id']

        # Create a distributed lock for the submission job
        lock = create_redis_lock(f'submission-job-{submission_id}')
        if not lock.acquire(blocking=False):
            continue

        # Log that we are inspecting the pipeline
        logger.debug(f'inspecting pipeline: {job.metadata.name}')

        # Get database record of the submission
        submission: Submission = Submission.query.filter(
            Submission.id == submission_id,
        ).first()
        if submission is None:
            logger.error(f"submission from db not found {submission_id}")
            continue

        # Calculate job created time
        job_created = job.metadata.creation_timestamp.replace(tzinfo=None)

        # Delete the job if it is older than a few minutes
        if datetime.utcnow() - job_created > timedelta(minutes=autograde_pipeline_timeout_minutes):

            # Attempt to delete the k8s job
            reap_pipeline_job(job, submission)

        # If the job has finished, and was marked as successful, then
        # we can clean it up
        elif job.status.succeeded is not None and job.status.succeeded >= 1:

            # Attempt to delete the k8s job
            reap_pipeline_job(job, submission)

        lock.release()
