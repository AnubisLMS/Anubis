import docker

from .utils import report_error


def report(client, netid, assignment, submission, volume_name):
    """
    Report results of tests to api

    :client docker.client: docker clien
    :netid str: netid of student
    :assignment: name of assignment being tested
    :submission Submissions: id of submission
    :volume_name str: name of persistent volume
    """

    try:
        stdout=client.containers.run(
            'os3224-report',
            command=['python3', 'main.py', netid, assignment, str(submission.id)],
            network='traefik-proxy',
            remove=True,
            volumes={
                volume_name: {
                    'bind': '/mnt/submission',
                    'mode': 'rw',
                },
            },
        ).decode()
    except docker.errors.ContainerError as e:
        raise report_error('report failure', netid, assignment, submission.id)

