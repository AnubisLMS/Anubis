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


TODO re-document this whole procedure.
"""


def test_repo(repo_url, netid, assignment):
    """
    This function should launch the apropriate testing container
    for the assignment, passing along the function arguments.

    :repo_url str: url for student repo
    :netid str: netid of student
    :assignment str: name of assignment
    """

    client=docker.from_env()

    submission=Submissions(
        netid=netid,
        assignment=assignment,
    )

    try:
        db.session.add(submission)
        db.session.commit()
    except IntegrityError as e:
        # TODO handle integ err
        print('Unable to create submission', e)
        return False

    volume_name=client.volumes.create(
        name='submission-{}'.format(submission.id),
        driver='local',
    ).name

    clone(
        client,
        repo_url,
        volume_name
    )

    build(
        client,
        repo_url,
        netid,
        assignment,
        submission,
        volume_name
    )

    test(
        client,
        repo_url,
        netid,
        assignment,
        submission,
        volume_name
    )

    report(
        client,
        netid,
        assignment,
        submission.id,
        volume_name,
    )

    client.volumes.prune()
