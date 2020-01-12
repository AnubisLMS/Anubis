import docker
from sqlalchemy.exc import IntegrityError


def test(client, repo_url, netid, assignemtn, submission):
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
    """
    try:
        client.containers.run(
            'os3224-{}'.format(assignment),
            [repo_url, netid, assignment, submission.id],
            network_mode='none',
            privileged=True,
            volumes={
                '/mnt/submission': {
                    'bind': '/tmp/submission-{}'.format(
                        submission.id,
                    ),
                    'mode': 'rw',
                },
            },
        )
    except docker.errors.ContainerError as e:
        print('test crashed', e)
        # TODO handle this error



