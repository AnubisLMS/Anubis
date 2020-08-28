import logging
import logstash

from anubis.models import Submission
from kubernetes import client, config


def get_logger():
    logger = logging.getLogger('RPC-Worker')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(logstash.LogstashHandler('logstash', 5000))
    return logger

"""
This is where we should implement any and all job function for the
redis queue. The rq library requires special namespacing in order to work,
so these functions must reside in a separate file.
"""


def test_repo(submission_id: int):
    """
    This function should launch the appropriate testing container
    for the assignment, passing along the function arguments.

    :param submission_id: submission.id of to test
    """
    from anubis.app import create_app

    app = create_app()
    logger = get_logger()

    logger.info('Starting submission {}'.format(submission_id), extra={
        'submission_id': submission_id,
    })

    with app.app_context():
        submission = Submission.query.filter(
            Submission.id == submission_id).first()

        if submission is None:
            logger.error('Unable to find submission rpc.test_repo', extra={
                'submission_id': submission_id,
            })
            return

        logger.debug('Found submission {}'.format(submission_id), extra={'submission': submission.data})

        config.load_incluster_config()
        batch_v1 = client.BatchV1Api()

        container = client.V1Container(
            name="pipeline",
            image=submission.assignment.pipeline_image,
            env=[
                client.V1EnvVar(name="TOKEN", value=submission.token),
                client.V1EnvVar(name="COMMIT", value=submission.commit),
                client.V1EnvVar(name="GIT_REPO", value=submission.repo.repo_url),
                client.V1EnvVar(name="SUBMISSION_ID", value=str(submission.id))
            ],
            image_pull_policy='IfNotPresent'
        )
        # Create and configurate a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": "submission-pipeline", "role": "submission-pipeline-worker"}),
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]))
        # Create the specification of deployment
        spec = client.V1JobSpec(
            template=template,
            backoff_limit=4,
            ttl_seconds_after_finished=30)
        # Instantiate the job object
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name='submission-pipeline-{}'.format(submission.id)),
            spec=spec)

        logging.debug(job.to_str())

        batch_v1.create_namespaced_job(body=job, namespace='anubis')
