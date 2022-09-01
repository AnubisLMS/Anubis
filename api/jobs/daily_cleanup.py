from anubis.lms.courses import get_course_tas, get_course_professors, get_course_users, user_to_user_id_set
from anubis.models import (
    db,
    Course,
    InCourse,
    User,
)
from anubis.utils.data import with_context
from anubis.utils.logging import logger
from anubis.lms.assignments import get_recent_assignments
from anubis.lms.questions import fix_missing_question_assignments
from anubis.lms.courses import get_active_courses


def reap_ta_professor():
    """
    Find TAs and Professors that do not have an InCourse row
    for their course, and attempt to fix the problem.

    :return:
    """

    # Get all current courses
    courses: list[Course] = get_active_courses()

    # Iterate through all courses within the system
    for course in courses:

        # Get all students, professors and TAs for course
        students: list[User] = get_course_users(course)
        tas: list[User] = get_course_tas(course)
        profs: list[User] = get_course_professors(course)

        # Convert to user.id sets
        student_ids: set[str] = user_to_user_id_set(students)
        ta_ids: set[str] = user_to_user_id_set(tas)
        prof_ids: set[str] = user_to_user_id_set(profs)

        # Create a set of user ids that will need to have InCourse
        # objects created for them.
        students_to_add: set[str] = set()

        # Calculate which ta and professor ids exist outside of the
        # student ids. Theses ids are the users that are missing
        # InCourse rows.
        students_to_add = students_to_add.union(ta_ids.difference(student_ids))
        students_to_add = students_to_add.union(prof_ids.difference(student_ids))

        # Iterate through the users that need to have InCourse rows
        # added. Create new rows as we go.
        for user_id in students_to_add:
            # Log the creation
            logger.info(f'Adding user to course: user_id={user_id} course_id={course.id}')

            # Create new InCourse row
            in_course = InCourse(
                owner_id=user_id,
                course_id=course.id,
            )

            # Add row to session
            db.session.add(in_course)

    # Commit the changes (if there are any)
    db.session.commit()


def fix_question_assignments():
    """
    Attempt to fix missing question assignments.

    :return:
    """

    recent_assignments = get_recent_assignments()

    for assignment in recent_assignments:
        fix_missing_question_assignments(assignment)


@with_context
def reap():
    # Fix tas and professors missing InCourse
    reap_ta_professor()

    # Fix question assignments
    fix_question_assignments()


if __name__ == "__main__":
    print("")
    print("""
             ___
            /   \\\\
       /\\\\ | . . \\\\
     ////\\\\|     ||
   ////   \\\\\\ ___//\\
  ///      \\\\      \\
 ///       |\\\\      |     
//         | \\\\  \\   \\    
/          |  \\\\  \\   \\   
           |   \\\\ /   /   
           |    \\/   /    
           |     \\\\/|     
           |      \\\\|     
           |       \\\\     
           |        |     
           |_________\\  

""")
    reap()
