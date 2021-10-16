from sqlalchemy import func

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

if __name__ == "__main__":
    course_query = get_courses()
    # Course List
    print("Course Name\tCourse Code")
    for course in course_query:
        print(f"{course.name}\t{course.course_code}")
    
    print()
    # Number of users enrolled in at least on class this semester
    print("Total users enrolled in at least one course this semester")
    print(get_active_users_this_semester())

    print()
    # Number of IDEs opened this semester
    print("Total IDEs opened this semseter")
    print(get_ides_opened_this_semester())

    print()
    # Number of students for each course
    print("Course Name\tCourse Code\tTotal users enrolled")
    for course in course_query:
        user_count = get_course_user_count(course)
        print(f"{course.name}\t{course.course_code}\t{user_count}")

    print()
    # Number of IDEs opened for each course
    print("Course Name\tCourse Code\tTotal IDEs opened")
    for course in course_query:
        theia_count = get_course_theia_session_count(course)
        print(f"{course.name}\t{course.course_code}\t{theia_count}")