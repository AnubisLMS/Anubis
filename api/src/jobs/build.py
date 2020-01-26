from sqlalchemy.exc import IntegrityError
import subprocess
import requests
import docker
import time

from .utils import report_error, PipelineException
from ..models import Builds
from ..app import db


def build(client, repo_url, submission, volume_name):
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

    netid=submission.netid
    assignment=submission.assignment


    logs=''
    name = '{netid}-{commit}-{assignment}-{id}-build'.format(
        netid=submission.netid,
        commit=submission.commit,
        assignment=submission.assignment,
        id=submission.id,
    )

    try:
        container=client.containers.run(
            'os3224-build',
            name=name,
            detach=True,
            command=['/entrypoint.sh', repo_url, netid, assignment, str(submission.id)],
            network_mode='none',
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
            raise PipelineException('build failue')

    except PipelineException as e:
        raise report_error(str(e), submission.id)

    except requests.exceptions.ReadTimeout:
        # Kill container if it has reached its timeout
        container.kill()
        raise report_error(
            'build timeout\n'+container.logs().decode(),
            submission.id
        )

    finally:
        container=client.containers.get(name)
        container.remove(force=True)

    b=Builds(
        stdout=logs,
        submission=submission
    )

    try:
        db.session.add(b)
        db.session.commit()
    except IntegrityError as e:
        # TODO handle integ err
        return print(e)

    return b


