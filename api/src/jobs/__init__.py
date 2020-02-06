from sqlalchemy.exc import IntegrityError
import docker


from ..models import Submissions
from ..app import db


from .clone import clone
from .build import build
from .test import test
from .report import report
from .utils import report_error


"""
This is where we should implement any and all job function for the
redis queue. The rq library requires specical namespacing in order to work,
so these functions must reside in a seperate file.
"""


def test_repo(submission_id):
    """
    This function should launch the apropriate testing container
    for the assignment, passing along the function arguments.

    :repo_url str: url for student repo
    :netid str: netid of student
    :assignment str: name of assignment
    """

    client=docker.from_env()

    submission = Submissions.query.filter_by(
        id=submission_id
    ).first()
    repo_url = submission.repo

    volume_name=client.volumes.create(
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
