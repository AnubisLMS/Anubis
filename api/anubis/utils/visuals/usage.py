from datetime import datetime, timedelta
from typing import Optional, List

from anubis.models import Assignment, Course, TheiaImage
from anubis.utils.cache import cache
from anubis.utils.data import is_debug, is_job
from anubis.utils.logging import logger
from anubis.utils.usage.submissions import get_submissions
from anubis.utils.usage.theia import get_theia_sessions
from anubis.utils.usage.users import get_active_submission_users, get_active_theia_users
from anubis.utils.visuals.files import convert_fig_bytes
from anubis.utils.visuals.watermark import add_watermark


@cache.memoize(timeout=-1, forced_update=is_job, unless=is_debug)
def get_usage_plot(course_id: Optional[str]) -> Optional[bytes]:
    import matplotlib.colors as mcolors
    import matplotlib.pyplot as plt

    logger.info("GENERATING USAGE PLOT PNG")

    course: Course = Course.query.filter(Course.id == course_id).first()

    if course is None:
        return None

    assignments: List[Assignment] = Assignment.query.filter(
        Assignment.hidden == False,
        Assignment.release_date <= datetime.now(),
        Assignment.course_id == course_id,
    ).order_by(Assignment.release_date.desc()).all()
    submissions = get_submissions(course_id)
    theia_sessions = get_theia_sessions(course_id)

    fig, axs = plt.subplots(2, 1, figsize=(12, 10))

    # submissions over hour line
    ss = submissions.groupby(["assignment_id", "created"])["id"].count().reset_index().rename(
        columns={"id": "count"}
    ).groupby("assignment_id")

    # ides over hour line
    tt = theia_sessions.groupby(["assignment_id", "created"])["id"].count().reset_index().rename(
        columns={"id": "count"}
    ).groupby("assignment_id")

    assignment_colors = {
        assignment.id: color
        for assignment, color in zip(assignments, mcolors.TABLEAU_COLORS)
    }

    for key, group in ss:
        for assignment in assignments:
            if assignment.id == key:
                logger.info(f'PLOTTING ASSIGNMENT SUBMISSIONS = {assignment.id}')
                color = assignment_colors[assignment.id]
                axs[0].plot(group['created'], group['count'], color=color, label=None)
                axs[0].axvline(
                    x=assignment.due_date,
                    color=color,
                    linestyle="dotted",
                    label=f"{assignment.name}",
                )

    for key, group in tt:
        for assignment in assignments:
            if assignment.id == key:
                logger.info(f'PLOTTING ASSIGNMENT IDES = {assignment.id}')
                color = assignment_colors[assignment.id]
                axs[1].plot(group['created'], group['count'], color=color, label=None)
                axs[1].axvline(
                    x=assignment.due_date,
                    color=color,
                    linestyle="dotted",
                    label=f"{assignment.name}",
                )

    # Watermarks
    add_watermark(axs[0])
    add_watermark(axs[1])

    # Legends
    axs[0].legend(loc="upper left")
    axs[1].legend(loc="upper left")

    # Grids
    axs[0].grid(True)
    axs[1].grid(True)

    # Labels
    axs[0].set(
        title=f"{course.course_code} - Submissions over time",
        xlabel="time",
        ylabel="count",
    )
    axs[1].set(
        title=f"{course.course_code} - Cloud IDEs over time",
        xlabel="time",
        ylabel="count",
    )

    return convert_fig_bytes(plt, fig)


@cache.memoize(timeout=-1, forced_update=is_job, unless=is_debug)
def get_usage_plot_playgrounds():
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(12, 10))

    images = TheiaImage.query.filter().order_by(TheiaImage.id.desc()).all()
    theia_sessions = get_theia_sessions(None)
    s = theia_sessions.groupby(["image_id", "created"])["id"].count().reset_index().rename(
        columns={"id": "count"}
    ).groupby("image_id")
    for key, group in s:
        logger.info(key)
        for image in images:
            if image.id == key and image.public:
                ax.plot(group["created"], group["count"], label=image.title)

    add_watermark(ax)
    ax.legend()
    ax.grid()
    ax.set(
        title=f"Anubis Playgrounds - IDEs spawned per hour",
        xlabel="time",
        ylabel="IDEs spawned",
    )

    return convert_fig_bytes(plt, fig)


@cache.memoize(timeout=-1, forced_update=is_job, unless=is_debug)
def get_usage_plot_active(days: int = 14, step: int = 1):
    import matplotlib.pyplot as plt

    now = datetime.now().replace(hour=0, second=0, microsecond=0)
    start_datetime = now - timedelta(days=days - 1)

    xx = []
    total_y = []
    theia_y = []
    autograde_y = []

    for n in range(0, days, step):
        start_day = start_datetime + timedelta(days=n)
        end_day = start_day + timedelta(days=step - 1)
        submission_set = get_active_submission_users(start_day, end_day)
        theia_set = get_active_theia_users(start_day, end_day)
        xx.append(start_day)
        total_y.append(len(submission_set.union(theia_set)))
        autograde_y.append(len(submission_set))
        theia_y.append(len(theia_set))

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.plot(xx, total_y, 'b', label='Total users active on platform')
    ax.plot(xx, theia_y, 'r--', label='Total users that used Anubis IDE')
    ax.plot(xx, autograde_y, 'g--', label='Total users that used Anubis Autograder')
    ax.legend()

    add_watermark(ax)
    ax.set(
        title=f"Anubis LMS - Active users in the last {days} days - step {step} days",
        xlabel="time",
        ylabel="Users active",
    )
    ax.grid(True)

    return convert_fig_bytes(plt, fig)
