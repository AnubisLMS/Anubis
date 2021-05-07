from datetime import datetime
from typing import List, Union, Dict

from anubis.models import Submission, AssignmentRepo, User, db, Course, Assignment, InCourse
from anubis.utils.data import is_debug
from anubis.utils.http.https import error_response, success_response
from anubis.utils.services.cache import cache
from anubis.utils.services.rpc import enqueue_autograde_pipeline


def bulk_regrade_submission(submissions: List[Submission]) -> List[dict]:
    """
    Regrade a batch of submissions
    :param submissions:
    :return:
    """

    # Running list of regrade dictionaries
    response = []

    # enqueue regrade jobs for each submissions
    for submission in submissions:
        response.append(regrade_submission(submission, queue='regrade'))

    # Pass back a list of all the regrade return dictionaries
    return response


def regrade_submission(submission: Union[Submission, str], queue: str = 'default') -> dict:
    """
    Regrade a submission

    :param submission: Union[Submissions, str]
    :param queue:
    :return: dict response
    """

    # If the submission is a string, then we consider it to be a submission id
    if isinstance(submission, str):
        # Try to query for the submission
        submission = Submission.query.filter(
            Submission.id == submission,
        ).first()

        # If there was no submission found, then return an error status
        if submission is None:
            return error_response("could not find submission")

    # If the submission is already marked as in processing state, then
    # we can skip regrading this submission.
    if not submission.processed:
        return error_response("submission currently being processed")

    # Update the submission fields to reflect the regrade
    submission.processed = False
    submission.state = "regrading"
    submission.last_updated = datetime.now()

    # Reset the accompanying database objects
    submission.init_submission_models()

    # Enqueue the submission job
    enqueue_autograde_pipeline(submission.id, queue=queue)

    return success_response({
        "message": "regrade started"
    })


def fix_dangling():
    """
    Try to connect repos that do not have an owner.

    A dangling submission is a submission that has not been matched to
    a student. This happens when a student either does not give anubis
    a github username, or provides an incorrect one. When this happens,
    all submissions that come in for that repo are tracked, but not graded.

    The purpose of this function is to try to match assignment repos to
    submissions that lack an owner.

    :return:
    """

    # Running list of fixed submissions
    fixed = []

    # Find Assignment Repos that do not have an owner_id
    dangling_repos = AssignmentRepo.query.filter(
        AssignmentRepo.owner_id == None,
    ).all()

    # Iterate over all dangling repos
    for dangling_repo in dangling_repos:
        # Attempt to find an owner
        owner = User.query.filter(User.github_username == dangling_repo.github_username).first()

        # If an owner was found, then fix it
        if owner is not None:
            # Update the dangling repo
            dangling_repo.owner_id = owner.id
            db.session.add_all((dangling_repo, owner))
            db.session.commit()

            # Find all the submissions that belong to that
            # repo, fix then grade them.
            for s in dangling_repo.submissions:
                # Give the submission an owner
                s.owner_id = owner.id
                db.session.add(s)
                db.session.commit()

                # Update running tally of fixed submissions
                fixed.append(s.data)

                # Enqueue a autograde job for the submission
                enqueue_autograde_pipeline(s.id)

    # Find dangling submissions
    dangling_submissions = Submission.query.filter(Submission.owner_id == None).all()

    # Iterate through all submissions lacking an owner
    for s in dangling_submissions:
        # Try to find a repo to match
        dangling_repo = AssignmentRepo.query.filter(
            AssignmentRepo.id == s.assignment_repo_id
        ).first()

        # Try to find an owner student
        owner = User.query.filter(User.github_username == dangling_repo.github_username).first()

        # If an owner was found, then fix and regrade all relevant
        if owner is not None:
            # Give the repo an owner
            dangling_repo.owner_id = owner.id
            db.session.add_all((dangling_repo, owner))
            db.session.commit()

            # Give the submission an owner
            s.owner_id = owner.id
            db.session.add(s)
            db.session.commit()

            # Update running tally of fixed submissions
            fixed.append(s.data)

            # Enqueue a autograde job for the submission
            enqueue_autograde_pipeline(s.id)

    return fixed


@cache.memoize(timeout=3600, unless=is_debug)
def get_submissions(
        user_id=None, course_id=None, assignment_id=None
) -> Union[List[Dict[str, str]], None]:
    """
    Get all submissions for a given netid. Cache the results. Optionally specify
    a class_name and / or assignment_name for additional filtering.

    :param user_id:
    :param course_id:
    :param assignment_id: id of assignment
    :return:
    """

    # Load user
    owner = User.query.filter(User.id == user_id).first()

    # Verify user exists
    if owner is None:
        return None

    # Build filters
    filters = []
    if course_id is not None and course_id != "":
        filters.append(Course.id == course_id)
    if user_id is not None and user_id != "":
        filters.append(User.id == user_id)
    if assignment_id is not None:
        filters.append(Assignment.id == assignment_id)

    submissions = (
        Submission.query.join(Assignment)
            .join(Course)
            .join(InCourse)
            .join(User)
            .filter(Submission.owner_id == owner.id, *filters)
            .all()
    )

    return [s.full_data for s in submissions]