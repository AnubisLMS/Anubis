import requests
from sqlalchemy.exc import IntegrityError

import api.anubis.utils.elastic
from .utils import report_error, PipelineException
from .. import utils
from ..app import db
from ..models.submission import SubmissionBuild

assingment_files = {
    'os3224-assignment-1': ['xv6.img', 'fs.img', 'short', 'long'],
    'os3224-assignment-2': ['guess', 'linkedList'],
    'os3224-assignment-3': ['xv6.img', 'fs.img'],
    'midterm': ['xv6.img', 'fs.img', 'short', 'long'],
    'os3224-assignment-4': ['xv6.img', 'fs.img'],
    'final': ['xv6.img', 'fs.img'],
}


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

    netid = submission.netid
    assignment = submission.assignment.name

    logs = ''
    name = '{netid}-{commit}-{assignment}-{id}-build'.format(
        netid=submission.netid,
        commit=submission.commit,
        assignment=submission.assignment.name,
        id=submission.id,
    )

    try:
        container = client.containers.run(
            'os3224-build',
            name=name,
            detach=True,
            command=[
                        '/entrypoint.sh',
                        submission.commit,
                    ] + assingment_files[submission.assignment.name],
            network_mode='none',
            mem_limit='100m',
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
            raise PipelineException('build failure')

    except PipelineException as e:
        api.anubis.utils.elastic.esindex(
            type='build',
            logs=logs,
            submission=submission.id,
            netid=submission.netid,
        )
        raise report_error(str(e), submission.id)

    except requests.exceptions.ReadTimeout:
        # Kill container if it has reached its timeout
        api.anubis.utils.elastic.esindex(
            type='build-timeout',
            logs=logs,
            submission=submission.id,
            netid=submission.netid,
        )
        try:
            container.kill()
        except:
            pass
        raise report_error(
            'build timeout\n' + container.logs().decode(),
            submission.id
        )

    finally:
        container = client.containers.get(name)
        container.remove(force=True)

    b = SubmissionBuild(
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
