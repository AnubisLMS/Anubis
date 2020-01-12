from sqlalchemy.exc import IntegrityError
import docker
import shutil
import os

from ..models import Submissions
from .build import build
from .test import test
from .utils import report_results, report_error


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

    mount_location='/tmp/submission-{}'.format(
        submission.id,
    )

    os.makedirs(mount_location, exist_ok=True)

    build(
        client,
        repo_url,
        netid,
        assignment,
        submission,
        mount_location
    )

    test(
        client,
        repo_url,
        netid,
        assignment,
        submission,
        mount_location
    )

    report_results(
        mount_location,
        netid,
        assignment,
        submission.id,
    )

    shutil.rmtree(mount_location)

