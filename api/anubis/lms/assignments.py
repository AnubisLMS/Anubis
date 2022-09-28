from datetime import datetime, timedelta
from typing import Any
import string

from sqlalchemy import or_

from anubis.github.repos import create_assignment_group_repo, delete_assignment_repo
from anubis.lms.courses import (
    assert_course_admin,
    get_user_course_ids,
    is_course_admin,
    add_all_users_to_course,
    is_course_archived,
)
from anubis.lms.questions import ingest_questions
from anubis.models import (
    TheiaSession,
    AssignmentQuestion,
    AssignedStudentQuestion,
    AssignedQuestionResponse,
    Assignment,
    AssignmentRepo,
    AssignmentTest,
    Course,
    LateException,
    Submission,
    SubmissionTestResult,
    SubmissionBuild,
    User,
    db,
)
from anubis.utils.auth.user import verify_users
from anubis.utils.cache import cache
from anubis.utils.config import get_config_int
from anubis.utils.data import is_debug
from anubis.utils.data import req_assert


@cache.memoize(timeout=30, unless=is_debug)
def get_assignment_grace(assignment_id: str) -> datetime:
    assignment: Assignment = Assignment.query.filter(Assignment.id == assignment_id).first()
    return assignment.grace_date


@cache.memoize(timeout=30, unless=is_debug)
def get_assignment_due(assignment_id: str) -> datetime:
    assignment: Assignment = Assignment.query.filter(Assignment.id == assignment_id).first()
    return assignment.due_date


@cache.memoize(timeout=30)
def get_assignment_due_date(user_id: str, assignment_id: str, grace: bool = False) -> datetime:
    """
    Get the due date for an assignment for a specific user. We check to
    see if there is a late exception for this user, and return that if
    available. Otherwise, the default due date for the assignment is
    returned.

    :param user_id:
    :param assignment_id:
    :return:
    """

    # Get the slightly cached grace and due dates
    due_date: datetime = get_assignment_due(assignment_id)
    grace_date: datetime = get_assignment_grace(assignment_id)

    # If we are requesting the grace date, then we can just overwrite the
    # due date with the grace date
    if grace:
        due_date = grace_date

    # If there is no user signed in, then there is no late
    # exception to check for. Simply return the due date.
    if user_id is None:
        return due_date

    # Check for a late exception for this student
    late_exception: LateException | None = LateException.query.filter(
        LateException.owner_id == user_id,
        LateException.assignment_id == assignment_id,
    ).first()

    # If there was a late exception, return that due_date
    if late_exception is not None:
        return late_exception.due_date

    # If no late exception, return the assignment default
    return due_date


@cache.memoize(timeout=30, unless=is_debug)
def get_assignment_data(user_id: str, assignment_id: str) -> dict[str, Any] | None:
    assignment: Assignment = Assignment.query.filter(Assignment.id == assignment_id).first()

    if assignment is None:
        return None

    assignment_data = assignment.data
    fill_user_assignment_data(user_id, assignment_data)

    return assignment_data


def get_all_assignments(course_ids: set[str], admin_course_ids: set[str]) -> list[Assignment]:
    # Build a list of all the assignments visible
    # to this user for each of the specified courses.
    assignments: list[Assignment] = []

    # Get the assignment objects that should be visible to this user.
    regular_course_assignments = (
        Assignment.query.join(Course)
            .filter(
            Course.id.in_(list(course_ids.difference(admin_course_ids))),
            Assignment.release_date <= datetime.now(),
            Assignment.hidden == False,
        )
            .all()
    )

    # Get the assignment objects that should be visible to this user.
    admin_course_assignments = (
        Assignment.query.join(Course)
            .filter(
            Course.id.in_(list(admin_course_ids)),
        )
            .all()
    )

    # Add all the assignment objects to the running list
    assignments.extend(admin_course_assignments)
    assignments.extend(regular_course_assignments)

    return assignments


@cache.memoize(timeout=10, unless=is_debug, source_check=True)
def get_assignments(netid: str, course_id=None) -> list[dict[str, Any]] | None:
    """
    Get all the current assignments for a netid. Optionally specify a course_id
    to filter by course.

    :param netid: netid of user
    :param course_id: optional course name
    :return: list[Assignment.data]
    """
    # Load user
    user = User.query.filter_by(netid=netid).first()

    course_ids: set[str] = set()
    admin_course_ids: set[str] = set()

    # If course id was specified, then filter for a specific class
    if course_id is not None:
        if is_course_admin(course_id, user.id):
            admin_course_ids.add(course_id)
        else:
            course_ids.add(course_id)

    # If course_id was not specified, then pull assignments for all
    # courses that the user is in.
    else:
        admin_course_ids, course_ids = get_user_course_ids(user)

    course_ids = set(filter(lambda cid: not is_course_archived(cid), course_ids))

    # Get assignment objects
    assignments: list[Assignment] = get_all_assignments(course_ids, admin_course_ids)

    # Take all the sqlalchemy assignment objects,
    # and break them into data dictionaries.
    # Sort them by due_date.
    response = [
        _a.data
        for _a in sorted(
            assignments,
            reverse=True,
            key=lambda assignment: assignment.due_date,
        )
    ]

    # Add submission and repo information to the assignments
    for assignment_data in response:
        fill_user_assignment_data(user.id, assignment_data)

    return response


def assignment_sync(assignment_data: dict) -> tuple[dict | str, bool]:
    """
    Take an assignment_data dictionary from a assignment meta.yaml
    and update any and all existing data about the assignment.

    * This includes the assignment object fields, assignment tests,
    and assignment questions. *

    :param assignment_data:
    :return:
    """
    assignment = Assignment.query.filter(Assignment.unique_code == assignment_data["unique_code"]).first()

    # Attempt to find the class
    course_name = assignment_data.get("class", None) or assignment_data.get("course", None)
    course: Course = Course.query.filter(
        or_(
            Course.name == course_name,
            Course.course_code == course_name,
        )
    ).first()
    if course is None:
        return "Unable to find course", False

    assert_course_admin(course.id)

    # Check if it exists
    if assignment is None:
        assignment = Assignment(
            theia_image_id=course.theia_default_image_id,
            theia_options=course.theia_default_options,
            unique_code=assignment_data["unique_code"],
            course=course,
            hidden=True,
            description='',
            release_date=datetime.now() + timedelta(days=7),
            due_date=datetime.now() + timedelta(days=14),
            grace_date=datetime.now() + timedelta(days=14, hours=1),
        )

    # Update fields
    assignment.name = assignment_data["name"]
    assignment.pipeline_image = assignment_data["pipeline_image"]

    db.session.add(assignment)

    # Go through assignment tests, and delete those that are now
    # not in the assignment data.
    assignment_tests_names = [test['name'] for test in assignment_data["tests"]]
    for assignment_test in AssignmentTest.query.filter(
        AssignmentTest.assignment_id == assignment.id,
        AssignmentTest.name.notin_(assignment_tests_names),
    ).all():
        # Delete any and all submission test results that are still outstanding
        # for an assignment test that will be deleted.
        SubmissionTestResult.query.filter(
            SubmissionTestResult.assignment_test_id == assignment_test.id,
        ).delete()

        # Delete the assignment test
        AssignmentTest.query.filter(
            AssignmentTest.assignment_id == assignment.id,
            AssignmentTest.name == assignment_test.name,
        ).delete()

    # Run through the tests in the assignment data
    for test in assignment_data["tests"]:
        test_name = test['name']
        test_hidden = test['hidden']
        test_points = test['points']

        # Find if the assignment test exists
        assignment_test = (
            AssignmentTest.query.join(Assignment)
                .filter(
                Assignment.id == assignment.id,
                AssignmentTest.name == test_name,
            )
                .first()
        )

        # Create the assignment test if it did not already exist
        if assignment_test is None:
            assignment_test = AssignmentTest(assignment=assignment, name=test_name)
            db.session.add(assignment_test)

        assignment_test.hidden = test_hidden
        assignment_test.points = test_points

    # Sync the questions in the assignment data
    question_message = None
    if "questions" in assignment_data and isinstance(assignment_data["questions"], list):
        accepted, ignored, rejected = ingest_questions(assignment_data["questions"], assignment)
        question_message = {
            "accepted": accepted,
            "ignored": ignored,
            "rejected": rejected,
        }

    # Commit changes
    db.session.commit()

    return {"assignment": assignment.full_data, "questions": question_message}, True


def fill_user_assignment_data(user_id: str, assignment_data: dict[str, Any]):
    assignment_id: str = assignment_data["id"]

    # If the current user has a submission for this assignment, then mark it
    assignment_data["has_submission"] = (
        Submission.query.filter(
            Submission.assignment_id == assignment_id,
            Submission.owner_id == user_id,
        ).count()
        > 0
    )

    repo = AssignmentRepo.query.filter(
        AssignmentRepo.owner_id == user_id,
        AssignmentRepo.assignment_id == assignment_id,
        AssignmentRepo.repo_created == True,
        AssignmentRepo.collaborator_configured == True,
    ).first()

    # If the current user has a repo for this assignment, then mark it
    assignment_data["has_repo"] = repo is not None
    # If the current user has a repo for this assignment, then mark it
    assignment_data["repo_url"] = repo.repo_url if repo is not None else None

    due_date = get_assignment_due_date(user_id, assignment_id)
    assignment_data["past_due"] = due_date < datetime.now()
    assignment_data["due_date"] = str(due_date)


def get_active_assignment() -> list[Assignment]:
    return Assignment.query.filter(
        Assignment.release_date < datetime.now(),
        Assignment.due_date > datetime.now(),
        Assignment.hidden == False,
    ).all()


def get_recent_assignments(
    autograde_enabled: bool = None,
    delta: timedelta = None
) -> list[Assignment]:
    """
    Get recent assignments. Recent assignments based off of
    AUTOGRADE_RECALCULATE_DAYS config item value.

    :return:
    """

    filters = []

    if autograde_enabled:
        filters.append(Assignment.autograde_enabled == autograde_enabled)

    if delta is None:
        autograde_recalculate_days = get_config_int("AUTOGRADE_RECALCULATE_DAYS", default=60)
        autograde_recalculate_duration = timedelta(days=autograde_recalculate_days)

    else:
        autograde_recalculate_duration = delta

    recent_assignments = Assignment.query.filter(
        Assignment.due_date > datetime.now() - autograde_recalculate_duration,
        Assignment.due_date < datetime.now() + autograde_recalculate_duration,
        *filters,
    ).all()

    return recent_assignments


def delete_assignment_submissions(assignment: Assignment):
    """
    Delete Submissions & subtables

    :param assignment:
    :return:
    """
    submission_ids = db.session.query(Submission.id).filter(Submission.assignment_id == assignment.id)
    SubmissionTestResult.query.filter(SubmissionTestResult.submission_id.in_(submission_ids.subquery())).delete(
        synchronize_session=False
    )

    SubmissionBuild.query.filter(SubmissionBuild.submission_id.in_(submission_ids.subquery())).delete(
        synchronize_session=False
    )

    Submission.query.filter(
        Submission.assignment_id == assignment.id,
    ).delete(synchronize_session=False)


def delete_assignment_questions(assignment: Assignment):
    """
    Delete assignment questions & subtables

    :param assignment:
    :return:
    """
    assigned_question_ids = db.session.query(AssignmentQuestion.id).filter(
        AssignmentQuestion.assignment_id == assignment.id
    )
    AssignedQuestionResponse.query.filter(
        AssignedQuestionResponse.assigned_question_id.in_(assigned_question_ids.subquery())
    ).delete(synchronize_session=False)
    AssignedStudentQuestion.query.filter(AssignedStudentQuestion.assignment_id == assignment.id).delete(
        synchronize_session=False
    )
    AssignmentQuestion.query.filter(AssignmentQuestion.assignment_id == assignment.id).delete(synchronize_session=False)


def delete_assignment_repos(assignment: Assignment) -> None:
    repos: list[AssignmentRepo] = AssignmentRepo.query.filter(AssignmentRepo.assignment_id == assignment.id).all()

    for repo in repos:
        delete_assignment_repo(repo.owner, assignment, commit=False)


def delete_assignment(assignment: Assignment) -> None:
    """
    Delete an Anubis assignment. This function is unbelievably destructive.

    :param assignment:
    :return:
    """
    delete_assignment_submissions(assignment)
    delete_assignment_questions(assignment)
    delete_assignment_repos(assignment)

    # Delete assignment tests
    AssignmentTest.query.filter(AssignmentTest.assignment_id == assignment.id).delete(synchronize_session=False)

    # Delete theia sessions
    TheiaSession.query.filter(TheiaSession.assignment_id == assignment.id).delete(synchronize_session=False)

    # Delete assignment
    Assignment.query.filter(Assignment.id == assignment.id).delete(synchronize_session=False)

    db.session.commit()


def convert_group_netids_to_group_users(group_netids: list[list[str]]) -> tuple[list[User], list[list[User]]]:
    """

    :param group_netids:
    :return:
    """

    # Flatten groups into a single list of netids
    all_netids: list[str] = [netid for group in group_netids for netid in group]

    # Get a list of the found users, and set of not found netids
    users, not_found_netids = verify_users(all_netids)

    # Assert that all the netids are known. If they are not, eject from the request
    req_assert(
        len(not_found_netids) == 0,
        message="Action not complete. Netids are not known to Anubis: " + str(not_found_netids),
    )

    # netid -> User
    user_map = {user.netid: user for user in users}

    # Build groups of User objects from original groups of netids
    groups = []
    for netids in group_netids:
        group = []
        for netid in netids:
            group.append(user_map[netid])
        groups.append(group)

    return users, groups


def make_shared_assignment(assignment_id: str, group_netids: list[list[str]]) -> dict:
    """

    group_netids = [
      [netid1, netid2],
      [netid3]
    ]

    :param assignment_id:
    :param group_netids:
    :return:
    """

    assignment = Assignment.query.filter(
        Assignment.id == assignment_id,
    ).first()

    # Get users and groups
    users, groups = convert_group_netids_to_group_users(group_netids)

    # Make sure all users specified are in the course (add them if they are not)
    add_all_users_to_course(users, assignment.course)

    failed_to_create = []
    failed_to_configure = []

    all_repos = []
    for group in groups:
        if len(group) == 0:
            continue

        # Create the repo for the group
        repos = create_assignment_group_repo(group, assignment)

        # Track group
        all_repos.extend(repos)

        # Track repos that failed to create
        if not all(repo.repo_created for repo in repos):
            failed_to_create.append(",".join(user.netid for user in group))

        # Track repos that failed to have collaborators configured
        for repo in repos:
            if not repo.collaborator_configured:
                failed_to_configure.append(repo.owner.netid)

    req_assert(
        len(failed_to_configure) == 0 and len(failed_to_create) == 0,
        message=f"Failed to configure: {str(failed_to_configure)} \n" f"Failed to create: {str(failed_to_create)} \n",
    )

    return {
        "groups": [[user.netid for user in group] for group in groups],
        "repos": [repo.data for repo in all_repos],
    }


def get_assignment_tests(submission: Submission, only_visible=False):
    """
    Get a list of dictionaries of the matching Test, and TestResult
    for the current submission.

    :return:
    """

    # Construct query for
    query = SubmissionTestResult.query.join(AssignmentTest).filter(
        SubmissionTestResult.submission_id == submission.id,
    )

    # If only get visible tests, apply extra filter
    if only_visible:
        query.filter(AssignmentTest.hidden == False)

    # Query for matching AssignmentTests, and TestResults
    tests = query.all()

    # Convert to dictionary data
    return [{"test": result.assignment_test.data, "result": result.data} for result in tests]


def clean_assignment_name(assignment: Assignment) -> str:
    """
    Create short clean assignment name for places that require trimming

    :param assignment:
    :return:
    """

    assignment_name = assignment.name.lower().replace('-', '').replace('_', '')
    valid_charset = set(string.ascii_letters + string.digits)

    return ''.join(c for c in assignment_name if c in valid_charset)


