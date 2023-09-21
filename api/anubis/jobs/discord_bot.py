import os
import traceback
from datetime import datetime, timedelta
from io import BytesIO

import discord
from PIL import Image, ImageDraw, ImageFont
from dateutil.parser import parse as date_parse, ParserError
from discord.ext import commands
from sqlalchemy.sql import func
from tabulate import tabulate

from anubis.lms.courses import get_course_users
from anubis.models import db, Course, User, TheiaSession, InCourse, EmailEvent
from anubis.utils.data import with_context, human_readable_timedelta
from anubis.utils.visuals.usage import get_usage_plot_active


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
            len(get_course_users(course)),
            TheiaSession.query.join(Course).filter(Course.id == course.id).count()
        ]
        for course in Course.query.all()
    ]
    active_users = (
        User.query.join(InCourse, User.id == InCourse.owner_id)
        .join(Course, InCourse.course_id == Course.id)
        .distinct()
        .count()
    )
    ides_opened = TheiaSession.query.join(Course, TheiaSession.course_id == Course.id).count()

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


def get_day(day: str = None) -> datetime:
    try:
        return date_parse(day)
    except (ParserError, TypeError):
        print(traceback.format_exc())
        return datetime.now().replace(hour=0, minute=0, microsecond=0)


@with_context
def generate_active_plot(*args, **kwargs) -> BytesIO:
    return BytesIO(get_usage_plot_active(*args, **kwargs))


@with_context
def generate_health_report(mobile: bool = False) -> discord.Embed | Image.Image:
    from anubis.utils.healthcheck import healthcheck
    status, status_code = healthcheck()

    status_table = tabulate(
        [
            [k, v]
            for k, v in status.items()
        ],
        ["Test", "Status"]
    )

    report = f'Status Code: {status_code}\n\n{status_table}'

    if mobile:
        return to_image(report)
    return discord.Embed(
        title="Anubis Health",
        description=f"```{report}```"
    ).set_thumbnail(url=bot.user.avatar.url).set_author(name="Anubis Bot")


@with_context
def generate_ide_report(day=None, mobile: bool = False) -> discord.Embed | Image.Image:
    """
    Generate a report of the statuses of Anubis. The statuses are:
        Course names and code
        Number of students for each course
        Number of IDES opened for each course
        Number of active users this semester
        Number of IDEs opened this semester

    :return: The text of the report
    """

    today = get_day(day)
    this_week = today - timedelta(days=7)

    eod = today.replace(hour=23, minute=59, second=59, microsecond=0)
    now = datetime.now().replace(microsecond=0)

    # total_ide_seconds = get_ide_seconds(TheiaSession.created < eod)
    # week_ide_seconds = get_ide_seconds(
    #     TheiaSession.created < eod, TheiaSession.created > this_week
    # )
    # today_ide_seconds = get_ide_seconds(
    #     TheiaSession.created < eod, TheiaSession.created > today
    # )
    active_ides: list[TheiaSession] = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.created < eod
    ).order_by(TheiaSession.created).all()

    state_to_letter = {
        "Initializing":                               "I",
        "Waiting for IDE to be scheduled...":         "W.K8S",
        "Waiting for Persistent Volume to attach...": "W.PVC",
        "Waiting for IDE server to start...":         "W.IDE",
        "Running":                                    "R",
        "Failed":                                     "F",
    }

    data = tabulate(
        [
            [
                human_readable_timedelta(now - (ide.created if ide.created is not None else now)),
                human_readable_timedelta(now - (ide.last_proxy if ide.last_proxy is not None else now)),
                state_to_letter.get(ide.state, "U")
            ]
            for index, ide in enumerate(active_ides)
        ],
        ("Age", "Heartbeat", "State")
    )

    state_table = tabulate(
        [
            ["I", "Initializing"],
            ["W.K8S", "Scheduling"],
            ["W.PVC", "PVC"],
            ["W.IDE", "IDE Start"],
            ["R", "Running"],
            ["F", "Failed"],
        ],
        ("Letter", "State")
    )

    report = (
        "IDEs Active ({})\n{}\n\n{}"
    ).format(
        len(active_ides),
        data,
        state_table,
        # human_readable_timedelta(today_ide_seconds),
        # human_readable_timedelta(week_ide_seconds),
        # human_readable_timedelta(total_ide_seconds)
    )

    print(report)
    if mobile:
        if len(active_ides) > 20:
            report = report.split("\n")
            r1 = to_image("\n".join(report[:len(report) // 2]))
            r2 = to_image("\n".join(report[len(report) // 2:]))
            reportImg = Image.new("RGB", (r1.width + r2.width, max(r1.height, r2.height)))
            reportImg.paste(r1, (0, 0))
            reportImg.paste(r2, (r1.width, 0))
        else:
            reportImg = to_image(report)
        return reportImg
    return discord.Embed(
        title="IDE report",
        description="```" + report + "```"
    ).set_thumbnail(url=bot.user.avatar.url).set_author(name="Anubis Bot")


@with_context
def generate_email_report(day: str = None) -> discord.Embed | Image.Image:
    today = get_day(day)

    report = ""

    emails_total: int = EmailEvent.query.count()
    emails_today: int = EmailEvent.query.filter(EmailEvent.created > today).count()

    report += f"Emails Send Total: {emails_total}\n"
    report += f"Emails Send Today: {emails_today}\n"

    return discord.Embed(
        title="Email report",
        description="```" + report + "```"
    ).set_thumbnail(url=bot.user.avatar.url).set_author(name="Anubis Bot")


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    intents=intents,
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


@bot.command(name="active", help="Get current active plot.")
async def active_(ctx, days=14, step=1, *_):
    now = datetime.now().replace(microsecond=0)
    await ctx.send(
        file=discord.File(
            generate_active_plot(days=days, step=step),
            filename=f"anubis-active-14days-1step-{now.year}{now.month}{now.day}-{now.hour}{now.minute}{now.second}.png"
        )
    )


@bot.command(
    name="health", help="Anubis Healthcheck"
)
async def health_(ctx, *_):
    """
    Respond to `!report` command with a report of the statuses of Anubis

    :return:
    """
    if ctx.author.is_on_mobile():
        await ctx.send(
            file=discord.File(
                images_to_bytes(generate_health_report(mobile=True)),
                filename="health.png"
            )
        )
    else:
        await ctx.send(embed=generate_health_report())


@bot.command(
    name="ide", help="Anubis ide usage report. Use !ide mobile for mobile-friendly version"
)
async def ides_(ctx, day=None, *_):
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


@bot.command(
    name="email", help="Anubis email usage report."
)
async def email_(ctx, day=None, *_):
    """
    Respond to `!report` command with a report of the statuses of Anubis

    :return:
    """
    await ctx.send(embed=generate_email_report(day))


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
    ).set_thumbnail(url=bot.user.avatar.url)
    await ctx.send(embed=emb)


@bot.command(name="help", aliases=("commands",), help="Shows you this list")
async def help_(ctx, *args):
    """
    Respond to `!help` command with a list of valid commands and their descriptions

    :return:
    """
    emb = discord.Embed(
        title="Anubis Bot Help", description=""
    ).set_thumbnail(url=bot.user.avatar.url)
    for command in bot.commands:
        emb.add_field(name=bot.command_prefix + command.name, value=command.help)
    await ctx.send(embed=emb)


if __name__ == "__main__":
    bot.run(os.environ.get("DISCORD_BOT_TOKEN", default="DEBUG"))
