from datetime import datetime, timedelta

from anubis.models import Assignment, Course
from anubis.utils.data import with_context
from anubis.utils.visuals.assignments import get_assignment_sundial
from anubis.utils.visuals.usage import get_usage_plot, get_usage_plot_playgrounds, get_usage_plot_active
from anubis.utils.visuals.users import get_platform_users_plot


@with_context
def main():
    # Get courses with visuals enabled
    courses_with_visuals: list[Course] = Course.query.filter(
        Course.display_visuals == True
    ).all()

    # Generate usage plot for each course
    for course in courses_with_visuals:
        get_usage_plot(course.id)

    # Get recent assignments
    recent_assignments: list[Assignment] = Assignment.query.filter(
        Assignment.release_date > datetime.now(),
        Assignment.due_date < datetime.now() - timedelta(weeks=4)
    ).all()

    # Generate sundial for each
    for assignment in recent_assignments:
        get_assignment_sundial(assignment.id)

    # Generate playgrounds usage plot
    get_usage_plot_playgrounds()

    # Generate plot for active
    for days, step in [(14, 1), (90, 7), (180, 1), (365, 30)]:
        get_usage_plot_active(days=days, step=step)

    # Generate plot for last year registered users
    for days, step in [(365, 1), (365, 30)]:
        get_platform_users_plot(days=days, step=step)


if __name__ == "__main__":
    print(f"Running visuals job - {datetime.now()}")
    main()
