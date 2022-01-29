from datetime import datetime, timedelta
from typing import List

from anubis.models import Assignment, Course
from anubis.utils.data import with_context
from anubis.utils.visuals.assignments import get_assignment_sundial
from anubis.utils.visuals.usage import get_usage_plot, get_usage_plot_playgrounds


@with_context
def main():
    # Get courses with visuals enabled
    courses_with_visuals: List[Course] = Course.query.filter(
        Course.display_visuals == True
    ).all()

    # Generate usage plot for each course
    for course in courses_with_visuals:
        get_usage_plot(course.id)

    # Get recent assignments
    recent_assignments: List[Assignment] = Assignment.query.filter(
        Assignment.release_date > datetime.now(),
        Assignment.due_date < datetime.now() - timedelta(weeks=4)
    ).all()

    # Generate sundial for each
    for assignment in recent_assignments:
        get_assignment_sundial(assignment.id)

    # Generate playgrounds usage plot
    get_usage_plot_playgrounds()


if __name__ == "__main__":
    print(f"Running visuals job - {datetime.now()}")
    main()
