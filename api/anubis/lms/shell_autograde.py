import re

from anubis.constants import SHELL_AUTOGRADE_SUBMISSION_STATE_MESSAGE
from anubis.github.api import github_rest
from anubis.github.repos import split_github_repo_path, get_github_repo_default_branch
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
    return split_github_repo_path(assignment.shell_autograde_repo)


def verify_shell_exercise_repo_format(assignment: Assignment) -> bool:
    if assignment.shell_autograde_repo == '' or assignment.shell_autograde_repo is None:
        return True
    return split_shell_autograde_repo(assignment) is not None


def verify_shell_exercise_repo_allowed(assignment: Assignment) -> bool:
    if assignment.shell_autograde_repo == '' or assignment.shell_autograde_repo is None:
        return True
    allowed_orgs: list[str] = get_config_str('AUTOGRADE_SHELL_ALLOWED_ORGS', 'AnubisLMS,jepst').split(',')
    split_org_repo = split_shell_autograde_repo(assignment)
    if split_org_repo is None:
        return False
    org, _ = split_org_repo
    return org in allowed_orgs


def verify_shell_autograde_exercise_path_allowed(assignment: Assignment) -> bool:
    if assignment.shell_autograde_exercise_path == '' or assignment.shell_autograde_exercise_path is None:
        return True
    exercise_path_re = re.compile(r'^([a-zA-Z0-9\s_/-]+)/exercise.py$')
    return exercise_path_re.match(assignment.shell_autograde_exercise_path) is not None


def get_exercise_py_text(assignment: Assignment) -> str:
    # Split assignment repo name
    org, repo = split_shell_autograde_repo(assignment)

    default_branch = get_github_repo_default_branch(org, repo)
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
    # Verify basics
    req_assert(verify_shell_autograde_exercise_path_allowed(assignment))
    req_assert(verify_shell_exercise_repo_allowed(assignment))

    exercise_py_txt = get_exercise_py_text(assignment)

    assignment_name_re = re.compile(r"^\s*name=['\"]([a-zA-Z0-9 _-]+)['\"].*$", re.MULTILINE)
    exercise_name_match: list[str] = assignment_name_re.findall(exercise_py_txt)
    if len(exercise_name_match) == 0:
        logger.warning(f'Could not find assignment names based off of re {assignment.id=} {exercise_name_match=}')

    return exercise_name_match


@verbose_call()
def create_new_assignment_test_from_remote_exercises(assignment: Assignment, exercise_names: set[str]):
    for exercise_name in exercise_names:
        logger.info(f'Creating assignment test exercise for {exercise_name=}')
        exercise_assignment_test = AssignmentTest(
            assignment_id=assignment.id,
            name=exercise_name
        )
        db.session.add(exercise_assignment_test)
    db.session.commit()


@verbose_call()
def set_hidden_local_assignment_test_from_remote_exercises(
    assignment: Assignment,
    exercise_names: set[str],
    hidden: bool = True
):
    for exercise_name in exercise_names:
        logger.info(f'Setting {hidden=} for {exercise_name=}')
        AssignmentTest.query.filter(
            AssignmentTest.assignment_id == assignment.id,
            AssignmentTest.name == exercise_name
        ).update({'hidden': hidden})
    db.session.commit()


@verbose_call()
def set_assignment_test_order(
    remote_exercise_names: list[str],
):
    for index, exercise_name in enumerate(remote_exercise_names):
        AssignmentTest.query.filter(AssignmentTest.name == exercise_name).update({'order': index})
    db.session.commit()

@verbose_call()
@with_context
def autograde_shell_assignment_sync(assignment: Assignment):
    if not assignment.shell_autograde_enabled:
        logger.warning(f'Skipping shell autograde sync for {assignment=}')
        return

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

    logger.info(f'{remote_exercise_names=}')
    logger.info(f'{local_all_assignment_test_names=}')
    logger.info(f'{create_exercise_names=}')
    logger.info(f'{unhide_exercise_names=}')
    logger.info(f'{hide_exercise_names=}')

    set_hidden_local_assignment_test_from_remote_exercises(assignment, unhide_exercise_names, hidden=False)
    set_hidden_local_assignment_test_from_remote_exercises(assignment, hide_exercise_names, hidden=True)
    create_new_assignment_test_from_remote_exercises(assignment, create_exercise_names)
    set_assignment_test_order(remote_exercise_names_ordered)


def get_submission_test_results_map(submission: Submission) -> dict[str, SubmissionTestResult]:
    submission_test_results: list[SubmissionTestResult] = SubmissionTestResult.query.join(AssignmentTest).filter(
        SubmissionTestResult.submission_id == submission.id,
    ).order_by(AssignmentTest.order).all()
    return {
        submission_test_result.assignment_test.name: submission_test_result
        for submission_test_result in submission_test_results
    }


def resume_submission(submission: Submission) -> str:
    latest_submissions = get_latest_user_submissions(submission.assignment, submission.owner, limit=1, filter=[
        Submission.id != submission.id
    ])
    if len(latest_submissions) != 1:
        logger.info(f'skipping resume, no latest')
        return ''

    latest_submission: Submission = latest_submissions[0]
    logger.info(f'{latest_submission=}')

    assert latest_submission.id != submission.id

    last_submission_test_results: dict[str, SubmissionTestResult] = get_submission_test_results_map(latest_submission)
    current_submission_test_results: dict[str, SubmissionTestResult] = get_submission_test_results_map(submission)

    logger.info(f'{last_submission_test_results=}')
    logger.info(f'{current_submission_test_results=}')

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
    submission = Submission(
        id=default_id_factory(),
        owner_id=theia_session.owner_id,
        assignment_id=theia_session.assignment_id,
        assignment_repo_id=None,
        commit='fake-' + rand(40 - 5),
        state=SHELL_AUTOGRADE_SUBMISSION_STATE_MESSAGE,
    )
    theia_session.submission_id = submission.id
    db.session.add(submission)
    init_submission(submission, db_commit=True, state=SHELL_AUTOGRADE_SUBMISSION_STATE_MESSAGE)
    submission.build.passed = True
    submission.build.stdout = ''
    db.session.commit()
    return submission


def close_shell_autograde_ide_submission(theia_session: TheiaSession):
    submission = theia_session.submission
    submission.state = SHELL_AUTOGRADE_SUBMISSION_STATE_MESSAGE
    submission.processed = True
    db.session.add(submission)
