from sqlalchemy.exc import IntegrityError
import subprocess
import docker
import git

from ..models import Builds
from ..app import db


def clone(repo_url, path):
    """
    clone repo to path

    :repo_url str: url for repo
    :path str: path to clone repo to
    """
    return subprocess.check_call([
        'git',
        'clone',
        repo_url,
        path
    ])

def build(client, repo_url, netid, assignment, submission, mount_location):
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
    :mount_location str: path to persistent job mount
    """

    clone(repo_url, mount_location+'/xv6-public')

    try:
        stdout=client.containers.run(
            'os3224-build',
            command=['/entrypoint.sh', repo_url, netid, assignment, str(submission.id)],
            #remove=True,
            network_mode='none',
            volumes={
                mount_location: {
                    'bind': '/mnt/submission',
                    'mode': 'rw',
                },
            },
        ).decode()
    except docker.errors.ContainerError as e:
        # TODO handle this error
        return print('build crashed', e)

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


