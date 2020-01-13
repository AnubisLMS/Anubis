from sqlalchemy.exc import IntegrityError
import docker

from ..models import Tests
from ..app import db


def test(client, repo_url, netid, assignment, submission, mount_location):
    """
    Unlike the build container, not so many extra precautions
    need to be taken to ensure unintended behaviour. The
    containers need to run in privileged mode to leverage
    the host KVM. We still want to be careful to not
    let them phone home, so we will have them also run
    without networking capabilities.

    :client docker.client: docker client
    :repo_url str: url for student repo
    :netid str: netid of student
    :assignment: name of assignment being tested
    :submission Submissions: committed submission object
    :mount_location str: path to persistent job mount
    """

    try:
        stdout=client.containers.run(
            'os3224-assignment-{}'.format(assignment),
            command=['/entrypoint.sh', repo_url, netid, assignment, str(submission.id)],
            network_mode='none',
            #remove=True,
            privileged=True,
            volumes={
                mount_location: {
                    'bind': '/mnt/submission',
                    'mode': 'rw',
                },
            },
        ).decode()
    except docker.errors.ContainerError as e:
        print('test crashed', e)
        # TODO handle this error 

    t=Tests(
        stdout=stdout,
        submission=submission,
    )
    try:
        db.session.add(t)
        db.session.commit()
    except IntegrityError as e:
        print('unable to document test', e)
        # TODO handle this error

    return t



