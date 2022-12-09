import os
import time

from kubernetes import client, config

from anubis.k8s.pipeline.get import get_active_pipeline_jobs
from anubis.models import Submission, db
from anubis.utils.config import get_config_int
from anubis.utils.data import is_debug
from anubis.utils.logging import logger


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
        init_submission(submission, db_commit=True)

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


def create_pipeline_job_obj(submission: Submission) -> client.V1Job:
    """
    Create k8s job object for a submission pipeline.

    :param submission:
    :return:
    """

    # set some conservative resources requests and limits
    resource_requirements = {
        "limits":   {"cpu": "2", "memory": "750Mi"},
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
                "role":                   "submission-pipeline-worker",
                "network-policy":         "submission-pipeline",
                "submission-id":          submission.id,
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
            name="submission-pipeline-{}-{}".format(submission.owner.netid, int(time.time())),
            labels={
                "app.kubernetes.io/name": "submission-pipeline",
                "role":                   "submission-pipeline-worker",
                "submission-id":          submission.id,
            }
        ),
        spec=spec,
    )

    return job
