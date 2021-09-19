from typing import List

from datetime import datetime

from anubis.config import config
from anubis.models import Assignment, Course
from anubis.utils.data import with_context
from anubis.utils.visuals.assignments import get_assignment_sundial
from anubis.utils.visuals.usage import get_usage_plot


@with_context
def create_visuals(*_, **__):
    """
    Create visuals files to be cached in redis.

    :return:
    """

    course_with_visuals: List[Course] = Course.query.filter(
        Course.display_visuals == True,
    ).all()

    # Iterate over courses with display visuals enabled
    for course in course_with_visuals:

        # Generate a usage graph for each course. This operation is always run
        # and always cached when run in the visuals cronjob.
        get_usage_plot(course.id)

    # For recent assignments
    recent_assignments: List[Assignment] = Assignment.query.filter(
        Assignment.release_date > datetime.now(),
        Assignment.due_date > datetime.now() - config.STATS_REAP_DURATION,
    ).all()

    # Iterate over all recent assignments
    for assignment in recent_assignments:

        # Generate new sundial data
        get_assignment_sundial(assignment.id)
