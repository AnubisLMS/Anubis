from anubis.constants import REAPER_TXT
from anubis.lms.assignments import get_active_assignments
from anubis.lms.shell_autograde import autograde_shell_assignment_sync
from anubis.models import Assignment
from anubis.utils.data import with_context
from anubis.utils.logging import logger

@with_context
def autograde_shell_sync():
    active_assignments = get_active_assignments(Assignment.shell_autograde_enabled == True)

    logger.info(f'{active_assignments=}')

    for assignment in active_assignments:
        autograde_shell_assignment_sync(assignment)


@with_context
def reap():
    autograde_shell_sync()


if __name__ == '__main__':
    print(REAPER_TXT)

    reap()
