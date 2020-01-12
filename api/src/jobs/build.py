from sqlalchemy.exc import IntegrityError
from ..models import Build


def build(client, repo_url, netid, assignment, submission):
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
    """
    try:
        stdout=client.containers.run(
            'os3224-build'
            [repo_url, netid, assignment, submission.id],
            remove=True,
            network_mode='none',
            volumes={
                '/mnt/submission': {
                    'bind': '/tmp/submission-{}'.format(
                        submission.id,
                    ),
                    'mode': 'rw',
                },
            },
        ).decode()
    except docker.errors.ContainerError as e:
        # TODO handle this error
        return print('build crashed', e)

    b=Build(
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


