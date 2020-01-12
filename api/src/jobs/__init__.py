from sqlalchemy.exc import IntegrityError
import docker
import shutil
import os

from ..models import Submissions
from .build import build
from .test import test

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
        return print(e)

    mount_path='/tmp/submission-{}'.format(
        submission.id,
    )

    os.makedirs(mount_path, exist_ok=True)

    b=build(
        client,
        repo_url,
        netid,
        assignment,
        submission
    )

    test(
        client,
        repo_url,
        netid,
        assignment,
        submission
    )

    shutil.rmtree(mount_path)

