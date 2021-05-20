from datetime import datetime

from anubis.models import Assignment
from anubis.config import config
from anubis.utils.data import with_context
from anubis.utils.visuals.assignments import get_assignment_sundial
from anubis.utils.visuals.usage import get_usage_plot


@with_context
def create_visuals(*_, **__):
    """
    Create visuals files to be cached in redis.

    :return:
    """
    get_usage_plot()

    recent_assignments = Assignment.query.filter(
        Assignment.release_date > datetime.now(),
        Assignment.due_date > datetime.now() - config.STATS_REAP_DURATION,
    ).all()

    for assignment in recent_assignments:
        get_assignment_sundial(assignment.id)
