import logging

from anubis.models import Submission

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

    submission = Submission.query.filter(Submission.id == submission_id).first()
    if submission is None:
        logging.error('<Error Unable to find submission>',
                      extra={'location': 'test_repo', 'submission_id': submission_id})
        return

    assignment = submission.assignment

