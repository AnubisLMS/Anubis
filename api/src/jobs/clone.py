import docker

from .utils import report_error


def clone(client, repo_url, volume_name):
    """
    Clones the given repo onto the docker
    volume

    :repo_url str: url of git repo
    :volume_name str: name of docker volume
    """

    try:
        client.containers.run(
            'os3224-clone',
            command=['git', 'clone', repo_url, '/mnt/submission/xv6-public'],
            remove=True,
            volumes={
                volume_name: {
                    'bind': '/mnt/submission',
                    'mode': 'rw',
                },
            },
        )
    except docker.errors.ContainerError as e:
        raise report_error('clone failure', netid, assignment, submission.id)

