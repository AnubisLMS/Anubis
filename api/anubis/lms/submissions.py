from datetime import datetime

from anubis.constants import AUTOGRADE_DISABLED_MESSAGE
from anubis.lms.assignments import get_assignment_due_date
from anubis.models import (
    Assignment,
    AssignmentTest,
    Course,
    InCourse,
    Submission,
    SubmissionBuild,
    SubmissionTestResult,
    User,
    db,
)
from anubis.utils.cache import cache
from anubis.utils.data import is_debug, split_chunks, with_context
from anubis.utils.http import error_response, success_response
from anubis.utils.logging import logger


@with_context
def bulk_regrade_submissions(submissions: list[Submission]) -> list[dict]:
    """
    Regrade a batch of submissions
    :param submissions:
    :return:
    """

    # Running list of regrade dictionaries
    response = []

    # enqueue regrade jobs for each submissions
    for submission in submissions:
        response.append(regrade_submission(submission, queue="regrade"))

    # Pass back a list of all the regrade return dictionaries
    return response


def regrade_submission(submission: Submission | str, queue: str = "default") -> dict:
    """
    Regrade a submission

    :param submission: Union[Submissions, str]
    :param queue:
    :return: dict response
    """
    from anubis.rpc.enqueue import enqueue_autograde_pipeline

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
    submission.pipeline_log = None

    # Reset the accompanying database objects
    init_submission(submission)

    # Enqueue the submission job
    enqueue_autograde_pipeline(submission.id, queue=queue)

    return success_response({"message": "regrade started"})


@cache.memoize(timeout=3, unless=is_debug, source_check=True)
def get_submissions(
    user_id=None,
    course_id=None,
    assignment_id=None,
    limit=None,
    offset=None,
) -> tuple[list[dict[str, str]], int]:
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


def recalculate_late(assignment_id: str):
    assignment: Assignment = Assignment.query.filter(
        Assignment.id == assignment_id
    ).first()

    # Get all students in the class
    students: list[User] = User.query.join(InCourse).filter(
        InCourse.course_id == assignment.course_id
    ).all()

    logger.info(f'Recalculating late submissions for {assignment}')

    for student in students:
        logger.info(f'Recalculating late submissions for {student}')

        # Recalculate late for student
        recalculate_late_submissions(student, assignment)


def recalculate_late_submissions(student: User, assignment: Assignment):
    """
    Recalculate the submissions that need to be
    switched from accepted to rejected.

    :param student:
    :param assignment:
    :return:
    """
    from anubis.rpc.enqueue import rpc_enqueue

    # Get the due date for this student
    due_date = get_assignment_due_date(student.id, assignment.id, grace=True)

    # Get the submissions that need to be rejected
    reject_query = Submission.query.filter(
        Submission.created > due_date,
        Submission.accepted == True,
        Submission.assignment_id == assignment.id,
        Submission.owner_id == student.id,
    )

    # Get the submissions that need to be accepted
    accept_query = Submission.query.filter(
        Submission.created < due_date,
        Submission.accepted == False,
        Submission.assignment_id == assignment.id,
        Submission.owner_id == student.id,
    )

    logger.debug(f'found {reject_query.count()} {accept_query.count()} to flip for {student}')

    # Update rows, set accepted accordingly
    accept_query.update({'accepted': True})
    reject_query.update({'accepted': False})

    # Only reset/regrade of autograde turned on for assignment
    if assignment.autograde_enabled:
        s_accept = accept_query.all()
        s_reject = reject_query.all()

        # Go through, and reset and enqueue regrade
        s_accept_ids = list(map(lambda x: x.id, s_accept))
        for chunk in split_chunks(s_accept_ids, 32):
            rpc_enqueue(bulk_regrade_submissions, "regrade", args=[chunk])

        # Reject the submissions that need to be updated
        for submission in s_reject:
            reject_late_submission(submission)

    # Commit the changes
    db.session.commit()


def reject_late_submission(submission: Submission):
    """
    set all the fields that need to be set when
    rejecting a submission.

    * Does not commit changes *

    :return:
    """

    # Go through test results, and set them to rejected
    for test_result in submission.test_results:
        test_result: SubmissionTestResult
        test_result.passed = False
        test_result.message = "Late submissions not accepted"
        test_result.output = ""
        test_result.output_type = "text"
        db.session.add(test_result)

    # Go through build results, and set them to rejected
    submission.build.passed = False
    submission.build.stdout = "Late submissions not accepted"
    db.session.add(submission.build)

    # set the fields on self to be rejected
    submission.accepted = False
    submission.processed = True
    submission.state = "Late submissions not accepted"
    db.session.add(submission)


def init_submission(submission: Submission, db_commit: bool = True, state: str = "Waiting for resources...", verbose: bool = True):
    """
    Create adjacent submission models.

    :return:
    """

    if verbose:
        logger.debug("initializing submission {}".format(submission.id))

    # If the models already exist, yeet
    if len(submission.test_results) != 0:
        SubmissionTestResult.query.filter_by(submission_id=submission.id).delete()
    if submission.build is not None:
        SubmissionBuild.query.filter_by(submission_id=submission.id).delete()

    if db_commit:
        # Commit deletions (if necessary)
        db.session.commit()

    # Find tests for the current assignment
    tests = AssignmentTest.query.filter(
        AssignmentTest.assignment_id == submission.assignment_id
    ).order_by(AssignmentTest.order.asc()).all()

    if verbose:
        logger.debug("found tests: {}".format(list(map(lambda x: x.data, tests))))

    for test in tests:
        tr = SubmissionTestResult(submission_id=submission.id, assignment_test_id=test.id)
        db.session.add(tr)
    sb = SubmissionBuild(submission_id=submission.id)
    db.session.add(sb)

    submission.accepted = True
    submission.processed = False
    submission.state = state
    submission.errors = None
    db.session.add(submission)

    if db_commit:
        # Commit new models
        db.session.commit()


def get_latest_user_submissions(assignment: Assignment, user: User, limit: int = 3, filter: list = None) -> list[Submission]:
    filter = filter or []
    return Submission.query.filter(
        Submission.assignment_id == assignment.id,
        Submission.owner_id == user.id,
        *filter
    ).order_by(Submission.created.desc()).limit(limit).all()


def fix_submissions_for_autograde_disabled_assignment(assignment: Assignment):
    if assignment.autograde_enabled or assignment.shell_autograde_enabled:
        logger.warning(f'Skipping autograde disabled fix for assignment {assignment=}')
        return

    logger.info(f'Fixing autograde disabled submissions for {assignment=}')
    Submission.query.filter(Submission.assignment_id == assignment.id).update({
        'processed': True,
        'state': AUTOGRADE_DISABLED_MESSAGE
    })
    db.session.commit()

    if not assignment.accept_late:
        count = 0
        # Crudely filter out submissions to be fixed
        submissions: list[Submission] = Submission.query.filter(
            Submission.accepted == True,
            Submission.created > assignment.grace_date,
            Submission.assignment_id == assignment.id,
        # Order submissions by user so we get cache locality
        ).order_by(Submission.owner_id)
        for submission in submissions:
            # Querying due dates on all these submissions is going to create quite a few roundtrips
            # to the database, so having get_assignment_due_date cached is somewhat helpful.
            if submission.created > get_assignment_due_date(submission.owner_id, assignment.id, grace=True):
                count += 1
                submission.accepted = False
        db.session.commit()
        logger.info(f'Fixed {count} falsely accepted past-grace submissions for {assignment=}')


def get_submission_tests(submission: Submission, only_visible=False):
    """
    Get a list of dictionaries of the matching Test, and TestResult
    for the current submission.

    :return:
    """

    # Construct query for
    query = SubmissionTestResult.query.join(AssignmentTest).filter(
        SubmissionTestResult.submission_id == submission.id,
    ).order_by(AssignmentTest.order)

    # If only get visible tests, apply extra filter
    if only_visible:
        query.filter(AssignmentTest.hidden == False)

    # Query for matching AssignmentTests, and TestResults
    tests = query.all()

    # Convert to dictionary data
    return [{"test": result.assignment_test.data, "result": result.data} for result in tests]
