from anubis.constants import REAPER_TXT
from anubis.lms.assignments import get_recent_assignments
from anubis.lms.autograde import bulk_autograde, reap_assignment_double_deliveries
from anubis.utils.data import with_context
from anubis.utils.logging import logger
from anubis.utils.visuals.assignments import get_assignment_sundial


def autograde_recalculate():
    """
    Calculate stats for recent submissions

    :return:
    """

    recent_assignments = get_recent_assignments(autograde_enabled=True)

    logger.info('Recent assignments:')
    logger.info('\n'.join(' ' * 4 + assignment.name for assignment in recent_assignments))

    for assignment in recent_assignments:
        logger.info('Running bulk autograde on {:<20} :: {:<20}'.format(
            assignment.name,
            assignment.course.course_code,
        ))
        bulk_autograde(assignment.id, limit=None, offset=None)

    for assignment in recent_assignments:
        logger.info('Running sundial recalc on {:<20} :: {:<20}'.format(
            assignment.name,
            assignment.course.course_code,
        ))
        get_assignment_sundial(assignment.id)


def autograde_cleanup_doubles():
    recent_assignments = get_recent_assignments(autograde_enabled=True)

    for assignment in recent_assignments:
        reap_assignment_double_deliveries(assignment)


@with_context
def reap():
    autograde_recalculate()

    autograde_cleanup_doubles()


if __name__ == "__main__":
    logger.info(REAPER_TXT)

    reap()
