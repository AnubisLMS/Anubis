import traceback

from anubis.constants import REAPER_TXT
from anubis.github.fix import fix_github_missing_submissions, fix_github_broken_repos
from anubis.lms.courses import get_active_courses
from anubis.models import (
    Course,
)
from anubis.utils.data import with_context
from anubis.utils.logging import logger


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
    # Attempt to fix any broken github repo permissions
    fix_github_broken_repos()

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


@with_context
def reap():
    # Reap broken repos
    reap_github()


if __name__ == "__main__":
    print(REAPER_TXT)

    reap()
