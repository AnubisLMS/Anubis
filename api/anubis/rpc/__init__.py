import logging
import logstash
import time

from anubis.models import Submission, Config
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
    from anubis.utils.redis_queue import enqueue_webhook_rpc

    app = create_app()
    logger = get_logger()

    logger.info('Starting submission {}'.format(submission_id), extra={
        'submission_id': submission_id,
    })

    with app.app_context():
        max_jobs = Config.query.filter(Config.key == "MAX_JOBS").first()
        max_jobs = int(max_jobs.value) if max_jobs is not None else 10
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

        active_jobs = batch_v1.list_namespaced_job('anubis')
        for job in active_jobs.items:
            if job.status.succeeded is not None and job.status.succeeded >= 1:
                logging.info('deleting namespaced job {}'.format(job.metadata.name))
                batch_v1.delete_namespaced_job(
                    job.metadata.name,
                    job.metadata.namespace,
                    propagation_policy='Background')

        if len(active_jobs.items) > max_jobs:
            logging.info('TOO many jobs - re-enqueue {}'.format(submission_id), extra={'submission_id': submission_id})
            enqueue_webhook_rpc(submission_id)
            time.sleep(1)
            exit(0)

        container = client.V1Container(
            name="pipeline",
            image=submission.assignment.pipeline_image,
            image_pull_policy='Always',
            env=[
                client.V1EnvVar(name="TOKEN", value=submission.token),
                client.V1EnvVar(name="COMMIT", value=submission.commit),
                client.V1EnvVar(name="GIT_REPO", value=submission.repo.repo_url),
                client.V1EnvVar(name="SUBMISSION_ID", value=str(submission.id)),
                client.V1EnvVar(name="GIT_CRED",
                                value_from=client.V1EnvVarSource(
                                    secret_key_ref=client.V1SecretKeySelector(
                                        name='git',
                                        key='credentials'
                                    ))),
            ],
            resources=client.V1ResourceRequirements(
                limits={'cpu': '1', 'memory': '100Mi'},
                requests={'cpu': '1', 'memory': '100Mi'})
        )
        # Create and configurate a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": "submission-pipeline", "role": "submission-pipeline-worker"}),
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]))
        # Create the specification of deployment
        spec = client.V1JobSpec(
            template=template,
            backoff_limit=3,
            ttl_seconds_after_finished=30)
        # Instantiate the job object
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(name='submission-pipeline-{}'.format(submission.id)),
            spec=spec)

        logging.debug(job.to_str())

        batch_v1.create_namespaced_job(body=job, namespace='anubis')
