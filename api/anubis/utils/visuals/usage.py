from datetime import datetime, timedelta
from typing import Optional

from anubis.models import Assignment, Course, TheiaImage
from anubis.utils.cache import cache
from anubis.utils.data import is_debug, is_job
from anubis.utils.logging import logger
from anubis.utils.usage.submissions import get_submissions
from anubis.utils.usage.theia import get_theia_sessions
from anubis.utils.visuals.files import convert_fig_bytes
from anubis.utils.usage.users import get_active_submission_users, get_active_theia_users


def add_watermark(ax, utcnow):
    ax.text(
        0.97, 0.9, f"Generated {utcnow} UTC",
        transform=ax.transAxes, fontsize=12, color="gray", alpha=0.5,
        ha="right", va="center",
    )


@cache.memoize(timeout=-1, forced_update=is_job, unless=is_debug)
def get_usage_plot(course_id: Optional[str]) -> Optional[bytes]:
    import matplotlib.colors as mcolors
    import matplotlib.pyplot as plt

    logger.info("GENERATING USAGE PLOT PNG")

    course: Course = Course.query.filter(Course.id == course_id).first()

    if course is None:
        return None

    assignments = Assignment.query.filter(
        Assignment.hidden == False,
        Assignment.release_date <= datetime.now(),
        Assignment.course_id == course_id,
    ).all()
    submissions = get_submissions(course_id)
    theia_sessions = get_theia_sessions(course_id)

    fig, axs = plt.subplots(2, 1, figsize=(12, 10))

    legend_handles0 = []
    legend_handles1 = []

    # submissions over hour line
    submissions.groupby(["assignment_id", "created"])["id"].count().reset_index().rename(
        columns={"id": "count"}
    ).groupby("assignment_id").plot(x="created", label=None, ax=axs[0])

    # ides over hour line
    theia_sessions.groupby(["assignment_id", "created"])["id"].count().reset_index().rename(
        columns={"id": "count"}
    ).groupby("assignment_id").plot(x="created", label=None, ax=axs[1])

    # assignment release line
    for color, assignment in zip(mcolors.TABLEAU_COLORS, assignments):
        legend_handles0.append(
            axs[0].axvline(
                x=assignment.due_date,
                color=color,
                linestyle="dotted",
                label=f"{assignment.name}",
            )
        )
        legend_handles1.append(
            axs[1].axvline(
                x=assignment.due_date,
                color=color,
                linestyle="dotted",
                label=f"{assignment.name}",
            )
        )

    utcnow = datetime.utcnow().replace(microsecond=0)

    add_watermark(axs[0], utcnow)
    axs[0].legend(handles=legend_handles0, loc="upper left")
    axs[0].set(
        title=f"{course.course_code} - Submissions over time",
        xlabel="time",
        ylabel="count",
    )
    axs[0].grid(True)

    add_watermark(axs[1], utcnow)
    axs[1].legend(handles=legend_handles1, loc="upper left")
    axs[1].set(
        title=f"{course.course_code} - Cloud IDEs over time",
        xlabel="time",
        ylabel="count",
    )
    axs[1].grid(True)

    return convert_fig_bytes(plt, fig)


@cache.memoize(timeout=-1, forced_update=is_job, unless=is_debug)
def get_usage_plot_playgrounds():
    import matplotlib.pyplot as plt

    utcnow = datetime.utcnow().replace(microsecond=0)

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
    ax.legend()

    add_watermark(ax, utcnow)
    ax.set(
        title=f"Anubis Playgrounds - IDEs spawned per hour",
        xlabel="time",
        ylabel="IDEs spawned",
    )
    ax.grid(True)

    return convert_fig_bytes(plt, fig)


@cache.memoize(timeout=-1, forced_update=is_job, unless=is_debug)
def get_usage_plot_active(days: int = 7):
    import matplotlib.pyplot as plt

    utcnow = datetime.utcnow().replace(hour=0, second=0, microsecond=0)
    start_datetime = utcnow - timedelta(days=days)

    xx = []
    total_y = []
    theia_y = []
    autograde_y = []

    for n in range(days):
        day = start_datetime + timedelta(days=n)
        submission_set = get_active_submission_users(day)
        theia_set = get_active_theia_users(day)
        xx.append(day)
        total_y.append(len(submission_set) + len(theia_set))
        autograde_y.append(len(submission_set))
        theia_y.append(len(theia_set))

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.plot(xx, total_y, 'b', label='Total users active on platform')
    ax.plot(xx, autograde_y, 'g--', label='Total users that used Anubis Autograder')
    ax.plot(xx, theia_y, 'r--', label='Total users that used Anubis IDE')
    ax.legend()

    add_watermark(ax, utcnow)
    ax.set(
        title=f"Anubis LMS - Active users in the last {days} days",
        xlabel="time",
        ylabel="Users active",
    )
    ax.grid(True)

    return convert_fig_bytes(plt, fig)

