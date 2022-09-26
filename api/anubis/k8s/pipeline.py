import os
import time
import traceback
from datetime import datetime, timedelta

import kubernetes
from kubernetes import client, config
from pottery import Redlock

from anubis.models import Submission, db
from anubis.utils.config import get_config_int
from anubis.utils.data import is_debug
from anubis.utils.logging import logger
from anubis.utils.redis import create_redis_lock


def create_pipeline_job_obj(submission: Submission) -> client.V1Job:
    """
    Create k8s job object for a submission pipeline.

    :param submission:
    :return:
    """

    # set some conservative resources requests and limits
    resource_requirements = {
        "limits": {"cpu": "2", "memory": "750Mi"},
        "requests": {"cpu": "500m", "memory": "500Mi"},
    }

    # If we are running in debug mode (like in minikube) then
    # we should skip setting resource requests and limits.
    if is_debug():
        resource_requirements = {}

    # Create the pipeline container from the submission object
    container = client.V1Container(
        name="pipeline",
        image=submission.assignment.pipeline_image,
        image_pull_policy=os.environ.get("IMAGE_PULL_POLICY", default="Always"),
        # setup the environment to include everything necessary for the
        # pipeline to be able to clone, test and report to the pipeline api.
        env=[
            client.V1EnvVar(name="TOKEN", value=submission.token),
            client.V1EnvVar(
                name="GIT_CRED",
                value_from=client.V1EnvVarSource(
                    secret_key_ref=client.V1SecretKeySelector(name="git", key="credentials")
                ),
            ),
        ],
        args=[
            f"--prod",
            f"--netid={submission.owner.netid}",
            f"--commit={submission.commit}",
            f"--repo={submission.repo.repo_url}",
            f"--path=./student",
            f"--submission-id={submission.id}",
        ],
        # set the resource requirements
        resources=client.V1ResourceRequirements(**resource_requirements),
        # Add a security context to disable privilege escalation
        # security_context=client.V1SecurityContext(
        #     allow_privilege_escalation=False,
        # )
    )

    # Create and configure a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(
            labels={
                "app.kubernetes.io/name": "submission-pipeline",
                "role": "submission-pipeline-worker",
                "network-policy": "submission-pipeline",
                "submission-id": submission.id,
            }
        ),
        spec=client.V1PodSpec(
            restart_policy="Never",
            containers=[container],
            # Minimal service account with no extra permissions
            service_account_name='theia-ide',
            # Disable service information from being injected into the environment
            enable_service_links=False,
            # Don't mount service account tokens
            automount_service_account_token=False,
        ),
    )

    # Create the specification of deployment
    spec = client.V1JobSpec(template=template, backoff_limit=3, ttl_seconds_after_finished=300)

    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(
            name="submission-pipeline-{}".format(submission.id),
            labels={
                "app.kubernetes.io/name": "submission-pipeline",
                "role": "submission-pipeline-worker",
                "submission-id": submission.id,
            }
        ),
        spec=spec,
    )

    return job


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


def read_pipeline_job_log(job: client.V1Job) -> str:
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
        )[:(2**16)-1]
    except kubernetes.client.exceptions.ApiException:
        logger.error("failed to get pod logs, continuing" + traceback.format_exc())
        return 'UNABLE TO GET PIPELINE LOG'


def reap_pipeline_job(job: client.V1Job, submission: Submission):
    # Capture the pipeline log
    submission.pipeline_log = read_pipeline_job_log(job)
    db.session.add(submission)
    db.session.commit()

    # Attempt to delete the k8s job
    delete_pipeline_job(job)


def get_active_pipeline_jobs() -> list[client.V1Job]:
    batch_v1 = client.BatchV1Api()

    # Get all pipeline jobs in the anubis namespace
    jobs = batch_v1.list_namespaced_job(
        namespace="anubis",
        label_selector="app.kubernetes.io/name=submission-pipeline,role=submission-pipeline-worker",
    )
    return jobs.items


def reap_pipeline_jobs():
    """
    Runs through all jobs in the namespace. If the job is finished, it will
    send a request to the kube api to delete it. Number of active jobs is
    returned.

    :return: number of active jobs
    """

    # Get the batch v1 object so we can query for active k8s jobs
    batch_v1 = client.BatchV1Api()

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


def create_submission_pipeline(submission_id: str):
    """
    This function should launch the appropriate testing container
    for the assignment, passing along the function arguments.

    :param submission_id: submission.id of to test
    """
    from anubis.lms.submissions import init_submission
    from anubis.rpc.enqueue import enqueue_autograde_pipeline

    # Log the creation event
    logger.info(
        "Creating submission pipeline job {}".format(submission_id),
        extra={
            "submission_id": submission_id,
        },
    )

    # Calculate the maximum number of jobs allowed in the cluster
    max_jobs = get_config_int("PIPELINE_MAX_JOBS", default=10)

    # Initialize kube client
    config.load_incluster_config()

    # Cleanup finished jobs
    active_jobs = len(get_active_pipeline_jobs())

    if active_jobs > max_jobs:
        logger.info(
            "TOO many jobs - re-enqueue {}".format(submission_id),
            extra={"submission_id": submission_id},
        )
        enqueue_autograde_pipeline(submission_id)
        exit(0)

    # Get the database entry for the submission
    submission = Submission.query.filter(Submission.id == submission_id).first()

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
    submission.state = "Initializing Pipeline"
    db.session.commit()

    # Create k8s job object
    job = create_pipeline_job_obj(submission)

    # Log the pipeline job creation
    logger.debug("creating pipeline job: " + job.to_str())

    # Send to kube api
    batch_v1 = client.BatchV1Api()
    batch_v1.create_namespaced_job(body=job, namespace="anubis")
