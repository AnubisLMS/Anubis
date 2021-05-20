from datetime import datetime
from typing import List, Union, Dict, Optional, Tuple

from anubis.models import (
    db,
    User,
    Course,
    Submission,
    AssignmentRepo,
    SubmissionTestResult,
    AssignmentTest,
    SubmissionBuild,
    Assignment,
    InCourse,
    LateException,
)
from anubis.utils.data import is_debug, split_chunks
from anubis.utils.http.https import error_response, success_response
from anubis.utils.services.cache import cache
from anubis.utils.services.rpc import rpc_enqueue, enqueue_autograde_pipeline
from anubis.utils.lms.assignments import get_assignment_due_date
from anubis.rpc.batch import rpc_bulk_regrade
from anubis.utils.services.logger import logger


def bulk_regrade_submissions(submissions: List[Submission]) -> List[dict]:
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
    init_submission(submission)

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
            for submission in dangling_repo.submissions:
                # Give the submission an owner
                submission.owner_id = owner.id
                db.session.add(submission)
                db.session.commit()

                # Update running tally of fixed submissions
                fixed.append(submission.data)

                # Get the due date
                due_date = get_assignment_due_date(owner, dangling_repo.assignment)

                # Check if the submission should be accepted
                if dangling_repo.assignment.accept_late and submission.created < due_date:
                    # Enqueue a autograde job for the submission
                    enqueue_autograde_pipeline(submission.id)

                # Reject the submission if it was late
                else:
                    reject_late_submission(submission)

    # Find dangling submissions
    dangling_submissions = Submission.query.filter(Submission.owner_id == None).all()

    # Iterate through all submissions lacking an owner
    for submission in dangling_submissions:
        # Try to find a repo to match
        dangling_repo = AssignmentRepo.query.filter(
            AssignmentRepo.id == submission.assignment_repo_id
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
            submission.owner_id = owner.id
            db.session.add(submission)
            db.session.commit()

            # Update running tally of fixed submissions
            fixed.append(submission.data)

            # Get the due date
            due_date = get_assignment_due_date(owner, submission.assignment)

            # Check if the submission should be accepted
            if submission.assignment.accept_late and submission.created < due_date:
                # Enqueue a autograde job for the submission
                enqueue_autograde_pipeline(submission.id)

            # Reject the submission if it was late
            else:
                reject_late_submission(submission)

    return fixed


@cache.memoize(timeout=5, unless=is_debug, source_check=True)
def get_submissions(
        user_id=None, course_id=None, assignment_id=None, limit=None, offset=None,
) -> Optional[Tuple[List[Dict[str, str]], int]]:
    """
    Get all submissions for a given netid. Cache the results. Optionally specify
    a class_name and / or assignment_name for additional filtering.

    :param offset:
    :param limit:
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

    query = (
        Submission.query.join(Assignment)
            .join(Course)
            .join(InCourse)
            .join(User)
            .filter(Submission.owner_id == owner.id, *filters)
            .order_by(Submission.created.desc())
    )

    all_total = query.count()

    if limit is not None:
        query = query.limit(limit)
    if offset is not None:
        query = query.offset(offset)

    submissions = query.all()

    return [s.full_data for s in submissions], all_total


def recalculate_late_submissions(student: User, assignment: Assignment):
    """
    Recalculate the submissions that need to be
    switched from accepted to rejected.

    :param student:
    :param assignment:
    :return:
    """

    # Get the due date for this student
    due_date = get_assignment_due_date(student, assignment)

    # Get the submissions that need to be rejected
    s_reject = Submission.query.filter(
        Submission.created > due_date,
        Submission.accepted == True,
    ).all()

    # Get the submissions that need to be accepted
    s_accept = Submission.query.filter(
        Submission.created < due_date,
        Submission.accepted == False,
    ).all()

    # Go through, and reset and enqueue regrade
    s_accept_ids = list(map(lambda x: x.id, s_accept))
    for chunk in split_chunks(s_accept_ids, 32):
        rpc_enqueue(rpc_bulk_regrade, 'regrade', args=[chunk])

    # Reject the submissions that need to be updated
    for submission in s_reject:
        reject_late_submission(submission)

    # Commit the changes
    db.session.commit()


def reject_late_submission(submission: Submission):
    """
    Set all the fields that need to be set when
    rejecting a submission.

    * Does not commit changes *

    :return:
    """

    # Go through test results, and set them to rejected
    for test_result in submission.test_results:
        test_result: SubmissionTestResult
        test_result.passed = False
        test_result.message = 'Late submissions not accepted'
        test_result.stdout = ''
        db.session.add(test_result)

    # Go through build results, and set them to rejected
    submission.build.passed = False
    submission.build.stdout = 'Late submissions not accepted'
    db.session.add(submission.build)

    # Set the fields on self to be rejected
    submission.accepted = False
    submission.processed = True
    submission.state = "Late submissions not accepted"
    db.session.add(submission)


def init_submission(submission: Submission, commit: bool = True):
    """
    Create adjacent submission models.

    :return:
    """

    logger.debug("initializing submission {}".format(submission.id))

    # If the models already exist, yeet
    if len(submission.test_results) != 0:
        SubmissionTestResult.query.filter_by(submission_id=submission.id).delete()
    if submission.build is not None:
        SubmissionBuild.query.filter_by(submission_id=submission.id).delete()

    if commit:
        # Commit deletions (if necessary)
        db.session.commit()

    # Find tests for the current assignment
    tests = AssignmentTest.query.filter_by(assignment_id=submission.assignment_id).all()

    logger.debug("found tests: {}".format(list(map(lambda x: x.data, tests))))

    for test in tests:
        tr = SubmissionTestResult(submission_id=submission.id, assignment_test_id=test.id)
        db.session.add(tr)
    sb = SubmissionBuild(submission_id=submission.id)
    db.session.add(sb)

    submission.accepted = True
    submission.processed = False
    submission.state = "Waiting for resources..."
    db.session.add(submission)

    if commit:
        # Commit new models
        db.session.commit()
