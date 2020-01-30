from sqlalchemy.exc import IntegrityError
import requests
import docker

from .utils import PipelineException
from ..models import Tests
from ..app import db


def test(client, repo_url, submission, volume_name):
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
    :volume_name str: name of persistent volume
    """

    netid=submission.netid
    assignment=submission.assignment

    logs=''
    name = '{netid}-{commit}-{assignment}-{id}-test'.format(
        netid=submission.netid,
        commit=submission.commit,
        assignment=submission.assignment,
        id=submission.id,
    )

    try:
        container=client.containers.run(
            'os3224-assignment-{}'.format(assignment),
            name=name,
            command=['/entrypoint.sh', repo_url, netid, assignment, str(submission.id)],
            network_mode='none',
            detach=True,
            privileged=True,
            volumes={
                volume_name: {
                    'bind': '/mnt/submission',
                    'mode': 'rw',
                },
            },
        )

        container.wait(timeout=30)
        container.reload()
        logs = container.logs().decode()

        # Check that the container had a successful exit code
        if container.attrs['State']['ExitCode'] != 0:
            raise PipelineException('test failue')

    except PipelineException as e:
        raise report_error(str(e), submission.id)

    except requests.exceptions.ReadTimeout:
        # Kill container if it has reached its timeout
        container.kill()
        raise report_error(
            'test timeout\n' + container.logs().decode(),
            submission.id
        )

    finally:
        container=client.containers.get(name)
        container.remove(force=True)

    t=Tests(
        stdout=logs,
        submission=submission,
    )
    try:
        db.session.add(t)
        db.session.commit()
    except IntegrityError as e:
        print('unable to document test', e)
        raise report_error('error in documenting submission', submission.id)

    return t



