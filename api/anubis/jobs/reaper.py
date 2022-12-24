import json
import traceback
from datetime import datetime, timedelta

from anubis.constants import REAPER_TXT
from anubis.github.fix import fix_github_missing_submissions, fix_github_broken_repos
from anubis.lms.assignments import get_recent_assignments
from anubis.lms.courses import get_active_courses
from anubis.lms.students import get_students
from anubis.lms.submissions import fix_submissions_for_autograde_disabled_assignment
from anubis.lms.submissions import init_submission
from anubis.models import (
    db,
    Submission,
    SubmissionBuild,
    Course,
)
from anubis.rpc.enqueue import enqueue_autograde_pipeline, enqueue_ide_reap_stale, enqueue_pipeline_reap_stale
from anubis.utils.data import with_context
from anubis.utils.logging import logger
from anubis.constants import SHELL_AUTOGRADE_SUBMISSION_STATE_MESSAGE

def reap_stale_submissions():
    """
    This will set find stale submission and set them to processed. A stale
    submission is one that has not been updated in 15 minutes and is still
    in a processing state.

    Flask app context is required before calling this function.

    :return:
    """

    print("Reaping stale submissions")

    # Find and update stale submissions
    Submission.query.filter(
        Submission.last_updated < datetime.now() - timedelta(minutes=60),
        Submission.processed == False,
        ~Submission.state.in_(['regrading', SHELL_AUTOGRADE_SUBMISSION_STATE_MESSAGE]),
    ).update({
        'processed': True,
        'state':     "Reaped after timeout",
    }, False)

    # Commit any changes
    db.session.commit()


def reap_recent_assignments():
    """
    Attempt to fix submissions in active (recent) assignments

    :return:
    """

    recent_assignments = get_recent_assignments()

    print(json.dumps({
        'reaping assignments:': [assignment.data for assignment in recent_assignments]
    }, indent=2))

    for assignment in recent_assignments:
        for submission in Submission.query.filter(
            Submission.assignment_id == assignment.id,
            Submission.build == None,
        ).all():
            if submission.build is None:
                init_submission(submission)
                enqueue_autograde_pipeline(submission.id)


def reap_github():
    """
    For reasons not clear to me yet, the webhooks are sometimes missing
    on the first commit. The result is that repos will be created on
    github without anubis seeing them.

    This function should be the fix for this. It will call out to the
    github api to list all the repos under the organization then try to
    create repos for each listed repo.

    :return:
    """

    # Pull all courses
    courses: list[Course] = get_active_courses()

    # Iterate over all course attempting to fix issues
    # on each github org.
    for course in courses:
        # Get the org_name from the matches values
        org_name = course.github_org

        if org_name is None or org_name == '':
            logger.warning(f'skipping fix_github_missing_submissions for course: {course.course_code}')
            continue

        # Attempt to fix any broken or lost repos for the course org.
        try:
            fix_github_missing_submissions(org_name)
        except Exception as e:
            logger.error('reaper.reap_broken_repos failed', org_name, e)
            logger.error(traceback.format_exc())
            logger.error('continuing')
            continue

    # Attempt to fix any broken github repo permissions
    fix_github_broken_repos()


def update_student_lists():
    """
    Iterate through all courses, updating the cached entry for
    the student lists in each.

    :return:
    """

    # Pull all courses
    courses: list[Course] = get_active_courses()

    # Iterate through courses, updating student list
    for course in courses:
        get_students(course.id)
    get_students(None)


def reap_autograde_disabled_submissions():
    for assignment in get_recent_assignments(autograde_enabled=False):
        fix_submissions_for_autograde_disabled_assignment(assignment)


def reap_shell_autograde_builds():
    logger.info(f'reap_shell_autograde_builds')
    for assignment in get_recent_assignments(autograde_enabled=True):
        if not assignment.shell_autograde_enabled:
            continue
        logger.info(f'reap_shell_autograde_builds {assignment=}')
        for submission in Submission.query.filter(Submission.assignment_id == assignment.id).all():
            SubmissionBuild.query.filter(SubmissionBuild.submission_id == submission.id).update({
                'passed': True,
                'stdout': ''
            })
        db.session.commit()


@with_context
def reap():
    # Enqueue a job to reap stale ide k8s resources
    enqueue_ide_reap_stale()

    # Enqueue a job to reap stale pipeline k8s resources
    enqueue_pipeline_reap_stale()

    # Reap the stale submissions
    reap_stale_submissions()

    # Reap broken repos
    reap_github()

    # Reap broken submissions in recent assignments
    reap_recent_assignments()

    # Update student lists
    update_student_lists()

    # Fix any submissions for autograde disabled assignments
    reap_autograde_disabled_submissions()

    # set builds to passed for shell autograde assignments
    reap_shell_autograde_builds()


if __name__ == "__main__":
    print(REAPER_TXT)

    reap()
