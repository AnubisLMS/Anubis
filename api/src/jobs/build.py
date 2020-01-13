from sqlalchemy.exc import IntegrityError
import subprocess
import docker

from .utils import report_error
from ..models import Builds
from ..app import db


def build(client, repo_url, netid, assignment, submission, volume_name):
    """
    Since we are running code that the students wrote,
    we need to take extra steps to prevent them from
    doing malicous stuff. The build container cant
    run in privileged mode, since that would be handing
    them a docker escape. Along with this, we need to
    make sure they cant becon or phone home. To prevent
    this, we can just run this in network_mode=none.

    :client docker.client: docker client
    :repo_url str: url for student repo
    :netid str: netid of student
    :assignment: name of assignment being tested
    :submission Submissions: committed submission object
    :volume_name str: name of persistent volume
    """

    try:
        stdout=client.containers.run(
            'os3224-build',
            command=['/entrypoint.sh', repo_url, netid, assignment, str(submission.id)],
            remove=True,
            network_mode='none',
            volumes={
                volume_name: {
                    'bind': '/mnt/submission',
                    'mode': 'rw',
                },
            },
        ).decode()
    except docker.errors.ContainerError as e:
        raise report_error('build failure', netid, assignment, submission.id)

    b=Builds(
        stdout=stdout,
        submission=submission
    )

    try:
        db.session.add(b)
        db.session.commit()
    except IntegrityError as e:
        # TODO handle integ err
        return print(e)

    return b


