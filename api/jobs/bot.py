import os
from typing import List
from datetime import datetime

import flask_sqlalchemy
from discord.ext import commands
from tabulate import tabulate
import discord

from anubis.models import Course, User, TheiaSession, InCourse
from anubis.utils.data import with_context


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
    report += "\n\nTotal IDEs opened this semseter\n"
    report += f"{get_ides_opened_this_semester()}"

    return report


def generate_ide_report() -> str:
    """
    Generate a report of the statuses of Anubis. The statuses are:
        Course names and code
        Number of students for each course
        Number of IDES opened for each course
        Number of active users this semester
        Number of IDEs opened this semester

    :return: The text of the report
    """

    today = datetime.today()
    eod = today.replace(hour=23, minute=59)

    all_ides_today = TheiaSession.query.filter(
        TheiaSession.created >= today,
        TheiaSession.created <= eod,
    ).all()

    active_ides: List[TheiaSession] = TheiaSession.query.filter(
        TheiaSession.active == True
    ).all()

    report = ''

    report += 'IDEs Currently Active ({})\n'.format(len(active_ides))
    report += tabulate(
        [
            [
                ide.id[:8],
                ide.course.course_code,
                str(ide.active),
                str(ide.autosave),
                str(ide.persistent_storage),
                str(ide.admin),
                str(ide.created),
                str(ide.last_proxy),
            ]
            for ide in active_ides
        ], headers=["ID", "Course Code", "Active", "Autosave", "Storage", "Admin", "Created", "Last Proxy"]
    )

    report += 'IDEs Active Today ({})\n'.format(len(all_ides_today))
    report += tabulate(
        [
            [
                ide.id[:8],
                ide.course.course_code,
                str(ide.active),
                str(ide.autosave),
                str(ide.persistent_storage),
                str(ide.admin),
                str(ide.created),
                str(ide.last_proxy),
            ]
            for ide in all_ides_today
        ], headers=["ID", "Course Code", "Active", "Autosave", "Storage", "Admin", "Created", "Last Proxy"]
    )

    # Number of IDEs opened this semester
    report += "\n\nTotal IDEs opened this semseter\n"
    report += f"{get_ides_opened_this_semester()}"

    return report


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
    await ctx.send("```" + generate_ide_report() + "```")


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
