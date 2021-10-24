import os
import asyncio
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
from anubis.utils.data import with_context
from anubis.models import Course, User, TheiaSession, InCourse

@with_context
def get_courses():
    return Course.query.filter(
        Course.name != "TEST", Course.name != "DEMO"
    )

@with_context
def get_active_users_this_semester():
    return User.query.join(
        InCourse, User.id==InCourse.owner_id
    ).join(
        Course, InCourse.course_id==Course.id
    ).filter(
        Course.name != "TEST", Course.name != "DEMO"
    ).distinct().count()

@with_context
def get_ides_opened_this_semester():
    return TheiaSession.query.join(
        Course, TheiaSession.course_id == Course.id
    ).count()

@with_context
def get_course_user_count(course):
    return User.query.join(
        InCourse, User.id == InCourse.owner_id
    ).join(
        Course, Course.id == InCourse.course_id
    ).filter(
        Course.id == course.id
    ).count()

@with_context
def get_course_theia_session_count(course):
    return TheiaSession.query.join(
        Course, TheiaSession.course_id==Course.id
    ).filter(
        Course.id == course.id
    ).count()

def generate_report():
    report = ""
    course_query = get_courses()
    # Course List
    report += "Course Name\tCourse Code\n"
    for course in course_query:
        report += f"{course.name}\t{course.course_code}\n"
    
    report += "\n"
    # Number of users enrolled in at least on class this semester
    report += "Total users enrolled in at least one course this semester\n"
    report += f"{get_active_users_this_semester()}\n"

    report += "\n"
    # Number of IDEs opened this semester
    report += "Total IDEs opened this semseter\n"
    report += f"{get_ides_opened_this_semester()}\n"

    report += "\n"
    # Number of students for each course
    report += "Course Name\tCourse Code\tTotal users enrolled\n"
    for course in course_query:
        user_count = get_course_user_count(course)
        report += f"{course.name}\t{course.course_code}\t{user_count}\n"

    report += "\n"
    # Number of IDEs opened for each course
    report += "Course Name\tCourse Code\tTotal IDEs opened\n"
    for course in course_query:
        theia_count = get_course_theia_session_count(course)
        report += f"{course.name}\t{course.course_code}\t{theia_count}\n"
    
    return report

bot = commands.Bot(command_prefix='!')
CHANNEL_ID = int(os.environ.get("DISCORD_CHANNEL_ID", "0"))
REPORT_TIME = time.fromisoformat(os.environ.get("DAILY_REPORT_TIME", "23:55:00"))
SLEEP_SECONDS = 15
SLEEP_SECONDS_REVERSE = SLEEP_SECONDS - timedelta(days=1).total_seconds()

@bot.command(name="report", help="Anubis Usage Report")
async def report(ctx):
    await ctx.send("```" + generate_report() + "```")

@tasks.loop(seconds=10)
async def daily_report():
    channel = bot.get_channel(CHANNEL_ID)

    now = datetime.now()
    today_report_time = datetime.combine(now.date(), REPORT_TIME)
    seconds = (today_report_time - now).total_seconds()

    if ((seconds > 0 and seconds <= SLEEP_SECONDS)
        or (seconds < 0 and seconds < SLEEP_SECONDS_REVERSE)):
        await asyncio.sleep(seconds)
        await channel.send(
            f"{str(today_report_time)} Daily Report:```{generate_report()}```"
        )

@bot.event
async def on_ready():
    daily_report.start()

if __name__ == "__main__":
    bot.run(os.environ.get("DISCORD_BOT_TOKEN", default="DEBUG"))