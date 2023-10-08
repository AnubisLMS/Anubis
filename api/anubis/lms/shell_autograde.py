import re

from anubis.constants import SHELL_AUTOGRADE_SUBMISSION_STATE_MESSAGE, SHELL_AUTOGRADE_SUBMISSION_NOT_DONE_MESSAGE
from anubis.github.api import github_rest
from anubis.github.repos import split_github_repo_path, get_github_repo_default_branch
from anubis.lms.assignments import get_assignment_due_date
from anubis.lms.submissions import get_latest_user_submissions
from anubis.lms.submissions import init_submission
from anubis.models import Assignment, AssignmentTest, TheiaSession, Submission, SubmissionTestResult, db
from anubis.models.id import default_id_factory
from anubis.utils.config import get_config_str
from anubis.utils.data import rand
from anubis.utils.data import with_context, req_assert
from anubis.utils.logging import verbose_call, logger
from anubis.utils.redis import create_redis_lock


def split_shell_autograde_repo(assignment: Assignment) -> tuple[str, str]:
    """
    ex: "AnubisLMS/Anubis" -> ("AnubisLMS", "Anubis")
    """
    return split_github_repo_path(assignment.shell_autograde_repo)


def verify_shell_exercise_repo_format(assignment: Assignment) -> bool:
    """
    Very high level spot check to make sure that assignment.shell_autograde_repo value
    is of a minimally valid string format. This does not check anything on github.
    """

    # If nothing entered, then it is valid
    if assignment.shell_autograde_repo == '' or assignment.shell_autograde_repo is None:
        return True

    # If we can split the string based off what we expect from a github repo format,
    # then it is of a minimally valid string format
    return split_shell_autograde_repo(assignment) is not None


def verify_shell_exercise_repo_allowed(assignment: Assignment) -> bool:
    """
    Allowed organizations is a very important step for us here. Since we are pulling and running code
    directly from github with no other verifications, we need to have a filter on allowed
    organizations / units of github.

    This function takes the entered repo for the source code of the assignment tests, and
    verifies that it is within an allowed set that is defined in the cluster key-value configuration.

    AUTOGRADE_SHELL_ALLOWED_ORGS
    """

    # If nothing entered, then there is nothing to do.
    if assignment.shell_autograde_repo == '' or assignment.shell_autograde_repo is None:
        return True

    # Split the repo string into organization and repo name
    split_org_repo = split_shell_autograde_repo(assignment)

    # If the split was unsuccessful, then the TA likely input an invalid repo string
    if split_org_repo is None:
        return False

    # Get the organization string
    org, _ = split_org_repo

    # Get the set of the allowed
    allowed_orgs: set[str] = set(get_config_str(
        'AUTOGRADE_SHELL_ALLOWED_ORGS',
        'AnubisLMS,jepst'
    ).split(','))

    # If the org is within the allowed set, then we are set to go
    return org in allowed_orgs


def verify_shell_autograde_exercise_path_allowed(assignment: Assignment) -> bool:
    """
    Very high level spot check to make sure that assignment.shell_autograde_exercise_path value
    is of a minimally valid string format. This does not check anything on github.
    """

    # If nothing set then it is allowed
    if assignment.shell_autograde_exercise_path == '' or assignment.shell_autograde_exercise_path is None:
        return True

    # Make sure the entered exercise.py path matches the path format we expect
    exercise_path_re: re.Pattern = re.compile(r'^([a-zA-Z0-9\s_/-]+)/exercise.py$')
    exercise_path_match: re.Match | None = exercise_path_re.match(assignment.shell_autograde_exercise_path)
    return exercise_path_match is not None


def get_exercise_py_text(assignment: Assignment) -> str:
    # Split assignment repo name
    org, repo = split_shell_autograde_repo(assignment)

    # Pull default branch from github.
    default_branch = get_github_repo_default_branch(org, repo)

    # Get the exercise.py text file.
    exercise_py_response: bytes = github_rest(
        f'/{org}/{repo}/{default_branch}/{assignment.shell_autograde_exercise_path}',
        api_domain='raw.githubusercontent.com',
        accept='text/plain',
    )
    exercise_py_txt = exercise_py_response.decode('ascii', errors='ignore')

    logger.debug(f'exercise_py_txt={exercise_py_txt}')
    return exercise_py_txt


@verbose_call()
def get_shell_assignment_remote_exercise_names(assignment: Assignment) -> list[str] | None:
    """
    Get list of assignment exercise names from remote github exercise.py file. Order of the tests
    is returned in this operation.
    """

    # Verify basics
    req_assert(verify_shell_autograde_exercise_path_allowed(assignment))
    req_assert(verify_shell_exercise_repo_allowed(assignment))

    # Get the string of exercise.py on github
    exercise_py_txt = get_exercise_py_text(assignment)

    ######
    # Perform a simple regex to extract the names of the tests. Ideally we would want to actually run
    # this python file, and extract the names from the structures defined within the code, but there is
    # no easy way to do this in an API or RPC instance where we would not be exposing credentials to
    # unvalidated code from github. It would be extremly reckless to run exercise.py code within any API
    # related instance.

    # Search for name=*
    assignment_name_re: re.Pattern = re.compile(
        r"^\s*name=['\"]([a-zA-Z0-9 :_-]+)['\"].*$",

        # Multiline flag is important here as we need to search for names line by line
        re.MULTILINE,
    )

    # Do multiline search for assignment names
    exercise_name_match: list[str] = assignment_name_re.findall(exercise_py_txt)

    # Verify that we actually found some. If not log a warning
    if len(exercise_name_match) == 0:
        logger.warning(f'Could not find assignment names based off of re {assignment.id=} {exercise_name_match=}')

    return exercise_name_match


@verbose_call()
def create_new_assignment_test_from_remote_exercises(
        assignment: Assignment,
        exercise_names: set[str],
        commit: bool = True,
):
    for exercise_name in exercise_names:
        logger.info(f'Creating assignment test exercise for {exercise_name=}')
        exercise_assignment_test = AssignmentTest(
            assignment_id=assignment.id,
            name=exercise_name
        )
        db.session.add(exercise_assignment_test)

    if commit:
        db.session.commit()


@verbose_call()
def set_hidden_local_assignment_test_from_remote_exercises(
        assignment: Assignment,
        exercise_names: set[str],
        hidden: bool = True,
        commit: bool = False,
):
    for exercise_name in exercise_names:
        logger.info(f'Setting {hidden=} for {exercise_name=}')
        AssignmentTest.query.filter(
            AssignmentTest.assignment_id == assignment.id,
            AssignmentTest.name == exercise_name
        ).update({'hidden': hidden})

    if commit:
        db.session.commit()


@verbose_call()
def set_assignment_test_order(
        assignment: Assignment,
        remote_exercise_names: list[str],
        commit=False,
):
    """
    Update the order of the tests for a given assignment
    """

    for index, exercise_name in enumerate(remote_exercise_names):
        AssignmentTest.query.filter(
            AssignmentTest.assignment_id == assignment.id,
            AssignmentTest.name == exercise_name,
        ).update({'order': index})

    if commit:
        db.session.commit()


@verbose_call()
@with_context
def autograde_shell_assignment_sync(assignment: Assignment):
    """
    This is an administrative level function called when a CI event triggers a sync of the assignment data.

    This is the high level function responsible for parsing the current state
    of the assignment test source code, and updating information within the anubis
    system to reflect these changes.
    """

    # Verify that the assignment we are looking at actually has the shell autograding turned on
    if not assignment.shell_autograde_enabled:
        logger.warning(f'Skipping shell autograde sync for {assignment=}')
        return

    # Use a distributed lock to make sure we dont step on any other process in the cluster's toes.
    # This will help with guaranteeing singular execution
    lock = create_redis_lock(f'assignment-shell-sync-{assignment.id}', auto_release_time=10.0)
    if not lock.acquire(blocking=False):
        return

    # Calculate remote exercise names from what is on github
    remote_exercise_names_ordered: list[str] = get_shell_assignment_remote_exercise_names(assignment)
    remote_exercise_names: set[str] = set(remote_exercise_names_ordered)

    # Calculate local names based off what is in the db
    local_visible_assignment_test_names: set[str] = {at.name for at in assignment.tests if at.hidden is False}
    local_hidden_assignment_test_names: set[str] = {at.name for at in assignment.tests if at.hidden is True}
    local_all_assignment_test_names: set[str] = local_visible_assignment_test_names.union(
        local_hidden_assignment_test_names
    )

    # Calculate what needs to be created, hidden, and un-hidden
    create_exercise_names = remote_exercise_names.difference(local_all_assignment_test_names)
    unhide_exercise_names = create_exercise_names.difference(local_hidden_assignment_test_names)
    hide_exercise_names = local_visible_assignment_test_names.difference(remote_exercise_names)

    # Log
    logger.info(f'{remote_exercise_names=}')
    logger.info(f'{local_all_assignment_test_names=}')
    logger.info(f'{create_exercise_names=}')
    logger.info(f'{unhide_exercise_names=}')
    logger.info(f'{hide_exercise_names=}')

    #####
    # Update what needs to be updated

    # Unhide any existing tests that have been added back
    set_hidden_local_assignment_test_from_remote_exercises(assignment, unhide_exercise_names, hidden=False)

    # Hide tests that have been removed (to preserve history)
    set_hidden_local_assignment_test_from_remote_exercises(assignment, hide_exercise_names, hidden=True)

    # Create new assignment tests for relevant items
    create_new_assignment_test_from_remote_exercises(assignment, create_exercise_names)

    # Update the order of tests to preserve execution order
    set_assignment_test_order(assignment, remote_exercise_names_ordered)


def get_submission_test_results_map(submission: Submission) -> dict[str, SubmissionTestResult]:
    """
    Get the submission test results for a given submission. Map the name of the test to the
    test itself. This assumes that the name of the test is unique for the assignment.
    """

    # Pull submission test results
    submission_test_results: list[SubmissionTestResult] = SubmissionTestResult.query.join(AssignmentTest).filter(
        SubmissionTestResult.submission_id == submission.id,
    ).order_by(AssignmentTest.order).all()

    # assignment test name -> submission test results
    return {
        submission_test_result.assignment_test.name: submission_test_result
        for submission_test_result in submission_test_results
    }


def resume_submission(submission: Submission) -> str:
    """
    When a student starts the assignment, closes the IDE they are working on,
    then opens a new one, we need to "resume" the previous state of the submission.

    For us, this means finding their last submission, and marking already completed
    tasks of the current IDE's submission as done.

    This should be called when creating a new live autograde IDE.
    """

    # Find latest submission
    latest_submissions: list[Submission] = get_latest_user_submissions(
        submission.assignment,
        submission.owner,
        limit=1,
        filter=[Submission.id != submission.id],
    )

    # If no submission was found, then we can skip
    if len(latest_submissions) != 1:
        logger.info(f'skipping resume, no latest')
        return ''

    # Get latest submission from list
    latest_submission: Submission = latest_submissions[0]
    logger.info(f'{latest_submission=}')

    # Make sure we are not looking at the current submission
    assert latest_submission.id != submission.id

    # Pull test result object for each submission. Map the IDE of the test to the result itself.
    last_submission_test_results: dict[str, SubmissionTestResult] = get_submission_test_results_map(latest_submission)
    current_submission_test_results: dict[str, SubmissionTestResult] = get_submission_test_results_map(submission)

    # Log
    logger.info(f'{last_submission_test_results=}')
    logger.info(f'{current_submission_test_results=}')

    # We need to be careful to respect the linear order of the tests. In this context, we need to
    # update the tests that are already done, and figure out the test to "resume" on based off
    # this order.
    resume_test_name, resume_test_order = '', -1
    for current_test_name, current_submission_test_result in current_submission_test_results.items():
        last_submission_test_result = last_submission_test_results.get(current_test_name, None)
        if last_submission_test_result is None or not last_submission_test_result.passed:
            continue

        current_submission_test_result.passed = last_submission_test_result.passed
        current_submission_test_result.output = last_submission_test_result.output
        current_submission_test_result.output_type = last_submission_test_result.output_type
        current_submission_test_result.message = last_submission_test_result.message

        current_test_order = current_submission_test_result.assignment_test.order
        if current_submission_test_result.passed and current_test_order > resume_test_order:
            resume_test_name, resume_test_order = current_test_name, current_test_order

    return resume_test_name


def create_shell_autograde_ide_submission(theia_session: TheiaSession) -> Submission:
    """
    Create and attach relevant submission structures for an autograded IDE.
    """

    # Find the assignment for the theia_session
    assignment: Assignment = Assignment.query.filter(
        Assignment.id == theia_session.assignment_id
    ).first()

    # Figure out if we should accept the submission based
    # on the due date of the assignment.
    accepted = True
    if not assignment.accept_late:
        # Figure out if the current submission is late
        late = theia_session.created < get_assignment_due_date(
            theia_session.owner_id,
            theia_session.assignment_id,
            grace=True,
        )

        # accepted is if not late
        accepted = not late

    # Create the relevant submission
    submission = Submission(
        id=default_id_factory(),
        accepted=accepted,
        owner_id=theia_session.owner_id,
        assignment_id=assignment.id,
        assignment_repo_id=None,
        # Git commit does not make sense here, so we create a fake placeholder one.
        commit='fake-' + rand(40 - 5),
        state=SHELL_AUTOGRADE_SUBMISSION_STATE_MESSAGE,
    )
    theia_session.submission_id = submission.id
    db.session.add(submission)

    # Call init_submission to create submission substructures
    init_submission(submission, db_commit=True, state=SHELL_AUTOGRADE_SUBMISSION_STATE_MESSAGE)

    # The submission build does not make sense in a live autograded paradigm, so
    # we mark as passed, with no output.
    submission.build.passed = True
    submission.build.stdout = ''

    # Commit changes
    db.session.commit()

    return submission


def close_shell_autograde_ide_submission(theia_session: TheiaSession, commit: bool = False) -> None:
    """
    When an IDE has a submission attached to it, we need to make sure
    the state of the submission enters a valid closed state. This function
    closes the various things on submission related objects to make that happen.

    This should be called on when closing an IDE with a submission
    """

    # Grab submission
    submission: Submission = theia_session.submission

    # Set state to closed
    submission.state = SHELL_AUTOGRADE_SUBMISSION_STATE_MESSAGE

    # Mark as processed
    submission.processed = True

    # Close each test result
    for test_result in submission.test_results:

        # If the test has not been marked as passed, then we
        # can mark as not done here
        if test_result.passed is None:
            test_result.passed = False
            test_result.message = SHELL_AUTOGRADE_SUBMISSION_NOT_DONE_MESSAGE
            test_result.output = SHELL_AUTOGRADE_SUBMISSION_NOT_DONE_MESSAGE
            db.session.add(test_result)

    # Stage database change
    db.session.add(submission)

    if commit:
        db.session.commit()
