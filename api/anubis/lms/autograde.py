import logging
from datetime import datetime

from parse import parse
from sqlalchemy.sql import func, select

from anubis.env import env
from anubis.lms.students import get_students_in_class
from anubis.models import db, Assignment, AssignmentTest, Submission, SubmissionTestResult
from anubis.utils.cache import cache
from anubis.utils.data import is_debug, is_job
from anubis.utils.http import error_response
from anubis.utils.logging import logger


@cache.memoize(timeout=60, unless=is_debug, source_check=True)
def _get_assignment_test_count(assignment_id) -> int:
    return AssignmentTest.query.filter(
        AssignmentTest.assignment_id == assignment_id,
    ).count()


@cache.memoize(timeout=5, unless=is_debug, source_check=True, forced_update=is_job)
def autograde(student_id, assignment_id, max_time: datetime = None):
    """
    Get the stats for a specific student on a specific assignment.

    Pulls all submissions, then finds the most recent one that
    has the most tests that passed.

    * This function is heavily cached as it is IO intensive on the DB *

    :param student_id:
    :param assignment_id:
    :param max_time:
    :return:
    """

    # list of filters for submission query
    submission_filters = []

    # maximum time to check
    if max_time is not None:
        submission_filters.append(Submission.created <= max_time)

    # best is the best submission seen so far
    best = None

    # best_count is the most tests that have
    # passed for this student so far
    best_count = -1

    # Get the max number of assignment tests that can be passed
    # so we can stop early if we find a submission that has all
    # tests passing
    max_correct = _get_assignment_test_count(assignment_id)

    # Iterate over all submissions for this student, tracking
    # the best submission so far (based on number of tests passed).
    # We start from the oldest submission and move to the newest.
    for submission in (
        Submission.query.filter(
            Submission.assignment_id == assignment_id,
            Submission.owner_id == student_id,
            # Submission.processed == True,
            Submission.accepted == True,
            *submission_filters
        )
            .order_by(Submission.created.desc())
            .all()
    ):

        # Make a map to weed out duplicates
        results = dict()
        for result in submission.test_results:
            results[result.assignment_test_id] = results.get(result.assignment_test_id, result.passed)

        # Calculate the number of tests that passed in this submission
        correct_count = sum(map(lambda passed: 1 if passed else 0, results.values()))

        # If the number of passed tests in this assignment is as good
        # or better as the best seen so far, update the running best.
        if correct_count >= best_count:
            best_count = correct_count
            best = submission

        # If the number of passed tests is equal to the number
        # of tests then we can stop and use this assignment.
        if best_count == max_correct:
            break

    # return the submission id of the best if there is one, otherwise None
    return best.id if best is not None else None


def autograde_submission_result_wrapper(
    assignment: Assignment, user_id: str, netid: str, name: str, submission_id: str
) -> dict:
    """
    The autograde results require quite of bit more information than
    just the id of the best submission. This function takes some high level
    information about the best submission, and breaks it down into a large
    dictionary of all the relevant data for the autograde result.

    * The admin panel uses all this extra data added by this function *

    :param assignment:
    :param user_id:
    :param netid:
    :param name:
    :param submission_id:
    :return:
    """
    if submission_id is None:
        # no submission
        return {
            "id": netid,
            "user_id": user_id,
            "netid": netid,
            "name": name,
            "submission": None,
            "build_passed": False,
            "tests_passed": 0,
            "total_tests": 0,
            "tests_passed_names": [],
            "full_stats": None,
            "main": None,
            "commits": None,
            "commit_tree": None,
            "late": False,
        }

    else:
        submission = Submission.query.filter(Submission.id == submission_id).first()
        repo_path = parse("https://github.com/{}", submission.repo.repo_url)[0] if submission.repo else None
        best_count = sum(map(lambda x: 1 if x.passed else 0, submission.test_results))
        late = "past due" if assignment.due_date < submission.created else "on time"
        late = "past grace" if assignment.grace_date < submission.created else late
        return {
            "id": netid,
            "user_id": user_id,
            "netid": netid,
            "name": name,
            "submission": submission.admin_data,
            "build_passed": submission.build.passed if submission.build is not None else False,
            "tests_passed": best_count,
            "total_tests": len(submission.test_results),
            "tests_passed_names": [test.assignment_test.name for test in submission.test_results if test.passed],
            "full_stats": "https://{}/api/private/submission/{}".format(env.DOMAIN, submission.id),
            "main": "https://github.com/{}".format(repo_path),
            "commits": "https://github.com/{}/commits/main".format(repo_path),
            "commit_tree": "https://github.com/{}/tree/{}".format(repo_path, submission.commit),
            "late": late,
        }


@cache.memoize(timeout=60 * 60, unless=is_debug, forced_update=is_job)
def bulk_autograde(assignment_id, netids=None, offset=0, limit=20):
    """
    Bulk autograde an assignment. Optionally specify a subset of netids.

    The offset and limit are used here to have the results of this function
    move as a window of the results.

    * Calculating the autograde results is very IO intensive on the db. For this,
    these results are heavily cached. *

    :param assignment_id:
    :param netids:
    :param offset:
    :param limit:
    :return:
    """

    # Running list of the best submissions for each student
    bests = []

    # Find the assignment object
    assignment = (
        Assignment.query.filter_by(name=assignment_id).first() or Assignment.query.filter_by(id=assignment_id).first()
    )
    if assignment is None:
        return error_response("assignment does not exist")

    # Get the list of students to get autograde results for
    students = get_students_in_class(assignment.course_id, offset=offset, limit=limit)
    if netids is not None:
        students = filter(lambda x: x["netid"] in netids, students)

    # Run through each of the students, getting the autograde results for each
    for student in students:
        # Get the best submission for this student from this assignment
        submission_id = autograde(student["id"], assignment.id)
        bests.append(
            # Use the stats_wrapper function to add all the necessary
            # metadata for the submission.
            autograde_submission_result_wrapper(
                assignment,
                student["id"],
                student["netid"],
                student["name"],
                submission_id,
            )
        )

    return bests


def reap_assignment_double_deliveries(assignment: Assignment):
    if not (assignment.autograde_enabled or assignment.shell_autograde_enabled):
        return

    # Get the max number of assignment tests that can be passed
    # so we can stop early if we find a submission that has all
    # tests passing
    max_correct = _get_assignment_test_count(assignment.id)

    # Iterate over all submissions for this student, tracking
    # the best submission so far (based on number of tests passed).
    # We start from the oldest submission and move to the newest.
    for submission in (
        db.session.query(Submission)
            .filter(Submission.id.in_(
                select(SubmissionTestResult.submission_id)
                .select_from(SubmissionTestResult)
                .join(Submission)
                .where(Submission.assignment_id == assignment.id)
                .group_by(Submission.id)
                .having(func.count(SubmissionTestResult.id) > max_correct)
            ))
            .all()
    ):
        logger.info(f'Found {submission} {len(submission.test_results)}/{max_correct}')

        # Make a map of duplicates
        test_result: dict[str, list[SubmissionTestResult]] = dict()
        for result in submission.test_results:
            if result.assignment_test_id not in test_result:
                test_result[result.assignment_test_id] = [result]
            else:
                test_result[result.assignment_test_id].append(result)

        # Go through each set of duplicate tests
        for results in test_result.values():

            # If duplicates dont exist, skip
            if len(results) == 1:
                continue

            # Select SubmissionTestResult to save
            selected_result = results[0]
            for result in results:
                if result.passed is True:
                    selected_result = result
                    break

            # Figure out which results to drop
            delete_test_ids = {test.id for test in results}.difference({selected_result.id})
            logger.info(f'Dropping {delete_test_ids}')

            # Drop results
            SubmissionTestResult.query.filter(SubmissionTestResult.id.in_(delete_test_ids)).delete()
            db.session.commit()

