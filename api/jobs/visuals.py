from datetime import datetime, timedelta
from typing import List

from anubis.models import Assignment
from anubis.utils.data import with_context
from anubis.utils.visuals.assignments import get_assignment_sundial
from anubis.utils.visuals.usage import get_usage_plot


@with_context
def main():
    get_usage_plot()

    recent_assignments: List[Assignment] = Assignment.query.filter(
        Assignment.release_date > datetime.now(),
        Assignment.due_date < datetime.now() - timedelta(weeks=4)
    ).all()

    for assignment in recent_assignments:
        get_assignment_sundial(assignment.id)


if __name__ == "__main__":
    print(f"Running visuals job - {datetime.now()}")
    main()
