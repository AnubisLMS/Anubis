import os
from discord.ext import commands, tasks
from anubis.models import Course, User, TheiaSession, InCourse
from anubis.utils.data import with_context

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

def daily_report():
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
channel_id = int(os.environ.get("DISCORD_CHANNEL_ID", "0"))

@bot.command(name="report", help="Anubis Usage Report")
async def report(ctx):
    await ctx.send("```" + daily_report() + "```")

@bot.event
async def on_ready():
    channel = bot.get_channel(channel_id)
    await channel.send("Usage Report:```" + daily_report() + "```")


bot.run(os.environ.get("DISCORD_BOT_TOKEN", default="DEBUG"))