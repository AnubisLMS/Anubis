import os
from typing import List
from datetime import datetime, timedelta

import flask_sqlalchemy
from sqlalchemy.sql import func
from discord.ext import commands
from tabulate import tabulate
import discord

from anubis.models import db, Course, User, TheiaSession, InCourse
from anubis.utils.data import with_context, human_readable_datetime


@with_context
def get_courses() -> flask_sqlalchemy.BaseQuery:
    """
    A helper function that constructs query for courses

    :return: A query object with TEST and DEMO course filtered
    """
    return Course.query.filter(Course.name != "TEST", Course.name != "DEMO")


@with_context
def get_active_users_this_semester() -> int:
    """
    Count the number of users registered for at least one course this semester

    :return: The number of users registered for at least one course this semester
    """
    return (
        User.query.join(InCourse, User.id == InCourse.owner_id)
        .join(Course, InCourse.course_id == Course.id)
        .filter(Course.name != "TEST", Course.name != "DEMO")
        .distinct()
        .count()
    )


@with_context
def get_ides_opened_this_semester() -> int:
    """
    Count the total number of IDEs opened this semester

    :return: Total number of IDEs opened this semester
    """
    return TheiaSession.query.join(Course, TheiaSession.course_id == Course.id).count()


@with_context
def get_course_user_count(course) -> int:
    """
    Count the number of users registered for a course

    :param course: The course object
    :return: Number of users registered for this course
    """
    return (
        User.query.join(InCourse, User.id == InCourse.owner_id)
        .join(Course, Course.id == InCourse.course_id)
        .filter(Course.id == course.id)
        .count()
    )


@with_context
def get_course_theia_session_count(course) -> int:
    """
    Count the number of IDEs opened for a course this semester

    :param course: The course object
    :return: Number of IDEs opened this semester
    """
    return (
        TheiaSession.query.join(Course, TheiaSession.course_id == Course.id)
        .filter(Course.id == course.id)
        .count()
    )


def generate_report() -> str:
    """
    Generate a report of the statuses of Anubis. The statuses are:
        Course names and code
        Number of students for each course
        Number of IDES opened for each course
        Number of active users this semester
        Number of IDEs opened this semester

    :return: The text of the report
    """

    # Course List
    courses = get_courses()

    # Number of students, IDEs for each course
    data = [
        [
            course.name,
            course.course_code,
            get_course_user_count(course),
            get_course_theia_session_count(course),
        ]
        for course in courses
    ]

    report = tabulate(
        data, headers=["Course Name", "Course Code", "Users", "IDEs opened"]
    )

    # Number of users enrolled in at least one class this semester
    report += "\n\nTotal users enrolled in at least one course this semester\n"
    report += f"{get_active_users_this_semester()}"

    # Number of IDEs opened this semester
    report += "\n\nTotal IDEs opened this semester\n"
    report += f"{get_ides_opened_this_semester()}"

    return report


def get_ide_seconds(*filters) -> timedelta:
    ide_hours_inactive = db.session.query(
        func.sum(func.time_to_sec(func.timediff(TheiaSession.ended, TheiaSession.created)))
    ).filter(TheiaSession.active == False, *filters).first()
    ide_hours_active = db.session.query(
        func.sum(func.time_to_sec(func.timediff(func.now(), TheiaSession.created)))
    ).filter(TheiaSession.active == True, *filters).first()
    ide_hours_inactive_s = int(ide_hours_inactive[0] or 0)
    ide_hours_active_s = int(ide_hours_active[0] or 0)
    print('ide_hours_inactive_s={}'.format(ide_hours_inactive_s))
    print('ide_hours_active_s={}'.format(ide_hours_active_s))
    return timedelta(seconds=ide_hours_active_s+ide_hours_inactive_s)


@with_context
def generate_ide_report() -> discord.Embed:
    """
    Generate a report of the statuses of Anubis. The statuses are:
        Course names and code
        Number of students for each course
        Number of IDES opened for each course
        Number of active users this semester
        Number of IDEs opened this semester

    :return: The text of the report
    """

    today = datetime.now().replace(hour=0, minute=0)
    now = datetime.now().replace(microsecond=0)

    total_ide_seconds = get_ide_seconds()
    today_ide_seconds = get_ide_seconds(TheiaSession.created > today)

    active_ides: List[TheiaSession] = TheiaSession.query.filter(
        TheiaSession.active == True
    ).all()

    report = ''

    report += 'IDEs Currently Active ({})\n'.format(len(active_ides))
    report += tabulate(
        [
            [
                str(index),
                human_readable_datetime(now - ide.created),
                human_readable_datetime(now - ide.last_proxy),
            ]
            for index, ide in enumerate(active_ides)
        ], headers=["ID", "Age", "Last Proxy"]
    )
    report += '\n\n'
    report += 'IDE Time Served Today: {}\n'.format(human_readable_datetime(today_ide_seconds))
    report += 'IDE Time Served Total: {}\n'.format(human_readable_datetime(total_ide_seconds))

    print(report)

    return discord.Embed(
        title='IDE report',
        author='Anubis Bot',
        description="```" + report + "```"
    ).set_thumbnail(url=bot.user.avatar_url)


bot = commands.Bot(
    command_prefix="!",
    case_insensitive=True,
    help_command=None,
)


@bot.command(name="report", help="Anubis usage report")
async def report_(ctx, *args):
    """
    Respond to `!report` command with a report of the statuses of Anubis

    :return:
    """
    await ctx.send("```" + generate_report() + "```")


@bot.command(name="ide", help="Anubis ide usage report")
async def ides_(ctx, *args):
    """
    Respond to `!report` command with a report of the statuses of Anubis

    :return:
    """
    await ctx.send(embed=generate_ide_report())


@bot.command(name="contribute", aliases=("github",), help="Contributing to Anubis")
async def contribute_(ctx, *args):
    """
    Respond to `!contribute` command with a link to the GitHub repo

    :return:
    """
    desc = "Thanks for your interest in contributing to Anubis! We're always looking for new people to help"
    desc += " make Anubis even better. Please head to [our GitHub repo](https://github.com/anubislms/Anubis)."
    emb = discord.Embed(
        title="Contributing to Anubis",
        description=desc,
    ).set_thumbnail(url=bot.user.avatar_url)
    await ctx.send(embed=emb)


@bot.command(name="help", aliases=("commands",), help="Shows you this list")
async def help_(ctx, *args):
    """
    Respond to `!help` command with a list of valid commands and their descriptions

    :return:
    """
    emb = discord.Embed(title="Anubis Bot Help", description="").set_thumbnail(
        url=bot.user.avatar_url
    )
    for command in bot.commands:
        emb.add_field(
            name=bot.command_prefix + command.name, value=command.help, inline=True
        )
    await ctx.send(embed=emb)


if __name__ == "__main__":
    bot.run(os.environ.get("DISCORD_BOT_TOKEN", default="DEBUG"))
