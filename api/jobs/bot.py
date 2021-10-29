import os
import traceback
from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Union

import discord
import flask_sqlalchemy
from dateutil.parser import parse as date_parse, ParserError
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.sql import func
from tabulate import tabulate

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


def generate_report(mobile: bool = False) -> str:
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
    # Number of students, IDEs for each course
    data = [
        [
            course.name,
            course.course_code,
            get_course_user_count(course),
            get_course_theia_session_count(course)
        ]
        for course in get_courses()
    ]
    active_users = get_active_users_this_semester()
    ides_opened = get_ides_opened_this_semester()

    return (
        tabulate(data, ("Course Name", "Course Code", "Users", "IDEs opened"))
        + "\n\nTotal users enrolled in at least one course this semester\n"
        + f"{active_users}\n\nTotal IDES opened this semester\n{ides_opened}"
    )


def get_ide_seconds(*filters) -> timedelta:
    ide_hours_inactive = db.session.query(
        func.sum(func.time_to_sec(func.timediff(TheiaSession.ended, TheiaSession.created)))
    ).filter(TheiaSession.active == False, *filters).first()

    ide_hours_active = db.session.query(
        func.sum(func.time_to_sec(func.timediff(func.now(), TheiaSession.created)))
    ).filter(TheiaSession.active == True, *filters).first()

    ide_hours_inactive_s = int(ide_hours_inactive[0] or 0)
    ide_hours_active_s = int(ide_hours_active[0] or 0)
    print("ide_hours_inactive_s", ide_hours_inactive_s, sep="=")
    print("ide_hours_active_s", ide_hours_active_s, sep="=")
    return timedelta(seconds=ide_hours_active_s + ide_hours_inactive_s)


def to_image(report: str, desiredWidth: int = 0) -> Image:
    font = ImageFont.truetype("Roboto-Regular.ttf", 24)
    width, height = font.getsize_multiline(report)
    if desiredWidth:
        width = desiredWidth
    img = Image.new("RGB", (width + 8, height + 8))
    draw = ImageDraw.Draw(img)
    draw.multiline_text((2, 2), report, font=font)
    return img


def images_to_bytes(img: Image) -> BytesIO:
    # In order to send through discord, *must* wrap getvalue() in BytesIO()
    b = BytesIO()
    img.save(b, format="PNG")
    return BytesIO(b.getvalue())


@with_context
def generate_ide_report(day=None, mobile: bool = False) -> Union[discord.Embed, Image.Image]:
    """
    Generate a report of the statuses of Anubis. The statuses are:
        Course names and code
        Number of students for each course
        Number of IDES opened for each course
        Number of active users this semester
        Number of IDEs opened this semester

    :return: The text of the report
    """

    try:
        today = date_parse(day)
    except (ParserError, TypeError):
        print(traceback.format_exc())
        today = datetime.now().replace(hour=0, minute=0, microsecond=0)

    print("today", today)

    eod = today.replace(hour=23, minute=59, second=59, microsecond=0)
    now = datetime.now().replace(microsecond=0)

    total_ide_seconds = get_ide_seconds(TheiaSession.created < eod)
    today_ide_seconds = get_ide_seconds(
        TheiaSession.created < eod, TheiaSession.created > today
    )
    active_ides: List[TheiaSession] = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.created < eod
    ).all()

    data = tabulate(
        [
            [
                index,
                human_readable_datetime(now - ide.created),
                human_readable_datetime(now - ide.last_proxy),
            ]
            for index, ide in enumerate(active_ides)
        ],
        ("ID", "Age", "Last Proxy")
    )

    report_raw = (
        "IDEs Active ({})\n{}\n\nIDE Time Served Today: {}\nIDE Time Served Total: {}"
    ).format(
        len(active_ides),
        data,
        human_readable_datetime(today_ide_seconds),
        human_readable_datetime(total_ide_seconds)
    )

    print(report_raw)
    if mobile:
        if len(active_ides) > 20:
            report = report_raw.split("\n")
            r1 = to_image("\n".join(report[:len(report) // 2]))
            r2 = to_image("\n".join(report[len(report) // 2:]))
            reportImg = Image.new("RGB", (r1.width + r2.width, max(r1.height, r2.height)))
            reportImg.paste(r1, (0, 0))
            reportImg.paste(r2, (r1.width, 0))
        else:
            reportImg = to_image(report_raw)
        return reportImg
    return discord.Embed(
        title="IDE report",
        description="```" + report_raw + "```"
    ).set_thumbnail(url=str(bot.user.avatar_url)).set_author(name="Anubis Bot")


bot = commands.Bot(
    command_prefix="!",
    case_insensitive=True,
    help_command=None,
)


@bot.command(
    name="report", help="Anubis usage report. Use !report mobile for mobile-friendly version"
)
async def report_(ctx, platform="desktop", *args):
    """
    Respond to `!report` command with a report of the statuses of Anubis

    :return:
    """
    if ctx.author.is_on_mobile() or platform == "mobile":
        await ctx.send(
            file=discord.File(
                images_to_bytes(to_image(generate_report(True))),
                filename="report.png"
            )
        )
    else:
        await ctx.send(f"```{generate_report()}```")


@bot.command(
    name="ide", help="Anubis ide usage report. Use !ide mobile for mobile-friendly version"
)
async def ides_(ctx, day=None, *args):
    """
    Respond to `!report` command with a report of the statuses of Anubis

    :return:
    """
    if ctx.author.is_on_mobile():
        await ctx.send(
            file=discord.File(
                images_to_bytes(generate_ide_report(day, True)),
                filename="ide.png"
            )
        )
    else:
        await ctx.send(embed=generate_ide_report(day))


@bot.command(name="contribute", aliases=("github",), help="Contributing to Anubis")
async def contribute_(ctx, *args):
    """
    Respond to `!contribute` command with a link to the GitHub repo

    :return:
    """
    desc = (
        "Thanks for your interest in contributing to Anubis! We're always"
        " looking for new people to help make Anubis even better. Please"
        " head to [our GitHub repo](https://github.com/anubislms/Anubis)."
    )
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
    emb = discord.Embed(
        title="Anubis Bot Help", description=""
    ).set_thumbnail(url=bot.user.avatar_url)
    for command in bot.commands:
        emb.add_field(name=bot.command_prefix + command.name, value=command.help)
    await ctx.send(embed=emb)


if __name__ == "__main__":
    bot.run(os.environ.get("DISCORD_BOT_TOKEN", default="DEBUG"))
