import os
import flask_sqlalchemy
from discord.ext import commands
from anubis.utils.data import with_context
from anubis.models import Course, User, TheiaSession, InCourse

@with_context
def get_courses() -> flask_sqlalchemy.BaseQuery:
    """
    A helper function that constructs query for courses

    :return: A query object with TEST and DEMO course filtered
    """
    return Course.query.filter(
        Course.name != "TEST", Course.name != "DEMO"
    )

@with_context
def get_active_users_this_semester() -> int:
    """
    Count the number of users registered for at least one course this semester

    :return: The number of users registers for at least one course this
             semester
    """
    return User.query.join(
        InCourse, User.id==InCourse.owner_id
    ).join(
        Course, InCourse.course_id==Course.id
    ).filter(
        Course.name != "TEST", Course.name != "DEMO"
    ).distinct().count()

@with_context
def get_ides_opened_this_semester() -> int:
    """
    Count the total number of IDEs opened this semester

    :return: Total number of IDEs opened this semester
    """
    return TheiaSession.query.join(
        Course, TheiaSession.course_id == Course.id
    ).count()

@with_context
def get_course_user_count(course) -> int:
    """
    Count the number of users registered for a course

    :param course: The course object
    :return: Number of users registered for this course
    """
    return User.query.join(
        InCourse, User.id == InCourse.owner_id
    ).join(
        Course, Course.id == InCourse.course_id
    ).filter(
        Course.id == course.id
    ).count()

@with_context
def get_course_theia_session_count(course) -> int:
    """
    Count the number of IDEs opened for a course this semester

    :param course: The course object
    :return: Number of IDEs opened this semester
    """
    return TheiaSession.query.join(
        Course, TheiaSession.course_id==Course.id
    ).filter(
        Course.id == course.id
    ).count()

def generate_report() -> str:
    """
    Generate a report of the statusesof Anubis. The statuses are:
        Course names and code
        Number of active users this semester
        Number of IDEs opened this semester
        Number of students for each course
        Number of IDES opened for each course
    
    :return: The text of the report
    """
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

@bot.command(name="report", help="Anubis Usage Report")
async def report(ctx):
    """
    Respond to `!report` command with a report of the statuses of Anubis

    :return:
    """
    await ctx.send("```" + generate_report() + "```")

if __name__ == "__main__":
    bot.run(os.environ.get("DISCORD_BOT_TOKEN", default="DEBUG"))