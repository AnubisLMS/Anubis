import logging
import os
import time

import kubernetes
from kubernetes import client

from anubis.models import Submission
from anubis.utils.data import is_debug


def create_pipeline_job_obj(submission: Submission) -> client.V1Job:
    """
    Create k8s job object for a submission pipeline.

    :param submission:
    :return:
    """

    # Set some conservative resources requests and limits
    resource_requirements = {
        'limits': {"cpu": "2", "memory": "750Mi"},
        'requests': {"cpu": "500m", "memory": "100Mi"},
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

        # Setup the environment to include everything necessary for the
        # pipeline to be able to clone, test and report to the pipeline api.
        env=[
            client.V1EnvVar(name="NETID", value=submission.owner.netid),
            client.V1EnvVar(name="TOKEN", value=submission.token),
            client.V1EnvVar(name="COMMIT", value=submission.commit),
            client.V1EnvVar(name="GIT_REPO", value=submission.repo.repo_url),
            client.V1EnvVar(name="SUBMISSION_ID", value=str(submission.id)),
            client.V1EnvVar(
                name="GIT_CRED",
                value_from=client.V1EnvVarSource(
                    secret_key_ref=client.V1SecretKeySelector(
                        name="git", key="credentials"
                    )
                ),
            ),
        ],

        # Set the resource requirements
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
            }
        ),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
    )

    # Create the specification of deployment
    spec = client.V1JobSpec(
        template=template, backoff_limit=3, ttl_seconds_after_finished=30
    )

    # Instantiate the job object
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(
            name="submission-pipeline-{}-{}".format(submission.id, int(time.time()))
        ),
        spec=spec,
    )

    return job


def reap_pipeline_jobs() -> int:
    """
    Runs through all jobs in the namespace. If the job is finished, it will
    send a request to the kube api to delete it. Number of active jobs is
    returned.

    :return: number of active jobs
    """

    # Get the batch v1 object so we can query for active k8s jobs
    batch_v1 = client.BatchV1Api()

    # Get all pipeline jobs in the anubis namespace
    jobs = batch_v1.list_namespaced_job(
        namespace="anubis",
        label_selector="app.kubernetes.io/name=submission-pipeline,role=submission-pipeline-worker"
    )

    # Count the number of active jobs
    active_count = 0

    # Iterate through all pipeline jobs
    for job in jobs.items:

        # If the job has finished, and was marked as successful, then
        # we can clean it up
        if job.status.succeeded is not None and job.status.succeeded >= 1:

            # Log that we are cleaning up the job
            logging.info("deleting namespaced job {}".format(job.metadata.name))

            # Attempt to delete the k8s job
            try:
                batch_v1.delete_namespaced_job(
                    job.metadata.name,
                    job.metadata.namespace,
                    propagation_policy="Background",
                )
            except kubernetes.client.exceptions.ApiException:
                pass

        # If the job has not finished, then we increment the active_count
        # and continue
        else:
            active_count += 1

    return active_count
