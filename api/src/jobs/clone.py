import requests
import docker

from .utils import report_error, PipelineException
from .. import utils


def clone(client, repo_url, submission, volume_name):
    """
    Clones the given repo onto the docker
    volume

    :repo_url str: url of git repo
    :volume_name str: name of docker volume
    """

    logs=''
    name = '{netid}-{commit}-{assignment}-{id}-clone'.format(
        netid=submission.netid,
        commit=submission.commit,
        assignment=submission.assignment,
        id=submission.id,
    )

    try:
        container=client.containers.run(
            'os3224-clone',
            name=name,
            detach=True,
            command=['git', 'clone', repo_url, '/mnt/submission/build'],
            volumes={
                volume_name: {
                    'bind': '/mnt/submission',
                    'mode': 'rw',
                },
                '/root/.ssh': {
                    'bind': '/root/.ssh',
                    'mode': 'ro',
                },
            },
        )
        container.wait(timeout=10)
        container.reload()
        logs = container.logs().decode()

        # Check that the container had a successful exit code
        if container.attrs['State']['ExitCode'] != 0:
            raise PipelineException('clone failure')

    except PipelineException as e:
        utils.esindex(
            type='clone',
            logs=logs,
            submission=submission.id,
            netid=submission.netid,
        )
        raise report_error(str(e), submission.id)

    except requests.exceptions.ReadTimeout:
        utils.esindex(
            type='clone-timeout',
            logs=logs,
            submission=submission.id,
            netid=submission.netid,
        )
        # Kill container if it has reached its timeout
        container.kill()
        raise report_error('clone timeout\n', submission.id)

    finally:
        container=client.containers.get(name)
        container.remove(force=True)

