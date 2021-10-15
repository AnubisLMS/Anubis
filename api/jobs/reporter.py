from anubis.models import Course
from anubis.utils.data import with_context

@with_context
def get_courses():
    return Course.query.filter(
        Course.name != "TEST", Course.name != "DEMO"
    )

if __name__ == "__main__":
    for course in get_courses():
        print("Course Name\tCourse Code")
        print(f"{course.name}\t{course.course_code}")