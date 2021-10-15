from anubis.models import Course, User, TheiaSession
from anubis.utils.data import with_context

@with_context
def get_courses():
    return Course.query.filter(
        Course.name != "TEST", Course.name != "DEMO"
    )

@with_context
def get_active_users_this_semester():
    return User.query.join(User.in_course).distinct().count()

@with_context
def get_ides_opened_this_semester():
    return TheiaSession.query.join(
        Course, TheiaSession.course_id==Course.id
    ).count()

if __name__ == "__main__":
    # Course List
    print("Course Name\tCourse Code")
    for course in get_courses():
        print(f"{course.name}\t{course.course_code}")
    
    print()
    # Number of users enrolled in at least on class this semester
    print("Total users enrolled in at least one course this semester")
    print(get_active_users_this_semester())

    print()
    # Number of IDEs opened this semester
    print("Total IDEs opened this semseter")
    print(get_ides_opened_this_semester())