import docker

from anubis.models import Submission
from anubis.rpc.submission_pipeline.build import build
from anubis.rpc.submission_pipeline.build import build
from anubis.rpc.submission_pipeline.clone import clone
from anubis.rpc.submission_pipeline.report import report
from anubis.rpc.submission_pipeline.test import test
from anubis.rpc.submission_pipeline.utils import report_error

"""
This is where we should implement any and all job function for the
redis queue. The rq library requires special namespacing in order to work,
so these functions must reside in a separate file.
"""


def test_repo(submission_id: int):
    """
    This function should launch the appropriate testing container
    for the assignment, passing along the function arguments.

    :param submission_id: submission.id of to test
    """

    client = docker.from_env()
    client.volumes.prune()

    submission = Submission.query.filter_by(
        id=submission_id
    ).first()
    repo_url = submission.repo

    volume_name = client.volumes.create(
        name='submission-{}'.format(submission.id),
        driver='local',
    ).name

    clone(
        client,
        repo_url,
        submission,
        volume_name,
    )

    build(
        client,
        repo_url,
        submission,
        volume_name
    )

    test(
        client,
        repo_url,
        submission,
        volume_name
    )

    report(
        client,
        repo_url,
        submission,
        volume_name,
    )

    client.volumes.prune()
