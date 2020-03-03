from sqlalchemy.exc import IntegrityError
import requests
import docker

from .utils import PipelineException, report_error
from ..models import Tests
from ..app import db
from .. import utils

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
    assignment_name=submission.assignment.name

    logs=''
    name = '{netid}-{commit}-{assignment}-{id}-test'.format(
        netid=submission.netid,
        commit=submission.commit,
        assignment=assignment_name,
        id=submission.id,
    )

    try:
        container=client.containers.run(
            'os3224-assignment-{}'.format(assignment_name),
            name=name,
            command=['/entrypoint.sh', repo_url, netid, assignment_name, str(submission.id)],
            network_mode='none',
            detach=True,
            privileged=True,
            mem_limit='100m',
            volumes={
                volume_name: {
                    'bind': '/mnt/submission',
                    'mode': 'rw',
                },
            },
        )

        container.wait(timeout=60)
        container.reload()
        logs = container.logs().decode()

        # Check that the container had a successful exit code
        if container.attrs['State']['ExitCode'] != 0:
            raise PipelineException('test failure')

    except PipelineException as e:
        utils.esindex(
            type='test',
            logs=logs,
            submission=submission.id,
            netid=submission.netid,
        )
        raise report_error(str(e), submission.id)

    except requests.exceptions.ReadTimeout:
        # Kill container if it has reached its timeout
        utils.esindex(
            type='test-timeout',
            logs=logs,
            submission=submission.id,
            netid=submission.netid,
        )
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



