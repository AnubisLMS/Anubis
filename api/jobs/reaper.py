import json
import traceback
from datetime import datetime, timedelta
from typing import List

from anubis.models import db, Submission, Assignment, Course
from anubis.utils.data import with_context
from anubis.lms.autograde import bulk_autograde
from anubis.lms.submissions import init_submission
from anubis.utils.github.fix import fix_github_missing_submissions, fix_github_broken_repos
from anubis.utils.logging import logger
from anubis.utils.rpc import enqueue_ide_reap_stale, enqueue_autograde_pipeline
from anubis.utils.config import get_config_int


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
        Submission.state != 'regrading',
    ).update({
        'processed': True,
        'state': "Reaped after timeout",
    }, False)

    # Commit any changes
    db.session.commit()


def reap_recent_assignments():
    """
    Calculate stats for recent submissions

    :return:
    """

    autograde_recalculate_days = get_config_int('AUTOGRADE_RECALCULATE_DAYS', default=60)
    autograde_recalculate_duration = timedelta(days=autograde_recalculate_days)

    recent_assignments = Assignment.query.filter(
        Assignment.release_date > datetime.now(),
        Assignment.due_date > datetime.now() - autograde_recalculate_duration,
    ).all()

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

    for assignment in recent_assignments:
        bulk_autograde(assignment.id)


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
    courses: List[Course] = Course.query.all()

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


@with_context
def reap():
    # Enqueue a job to reap stale ide k8s resources
    enqueue_ide_reap_stale()

    # Reap the stale submissions
    reap_stale_submissions()

    # Reap broken repos
    reap_github()

    # Reap broken submissions in recent assignments
    reap_recent_assignments()


if __name__ == "__main__":
    print("")
    print("""
             ___
            /   \\\\
       /\\\\ | . . \\\\
     ////\\\\|     ||
   ////   \\\\\\ ___//\\
  ///      \\\\      \\
 ///       |\\\\      |     
//         | \\\\  \\   \\    
/          |  \\\\  \\   \\   
           |   \\\\ /   /   
           |    \\/   /    
           |     \\\\/|     
           |      \\\\|     
           |       \\\\     
           |        |     
           |_________\\  

""")
    reap()
