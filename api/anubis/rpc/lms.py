from typing import List

from anubis.utils.data import with_context
from anubis.utils.logging import logger


@with_context
def assign_missing_questions(user_id: str):
    from anubis.lms.questions import fix_missing_question_assignments
    from anubis.models import User, Course, InCourse, Assignment

    # Log RPC job start
    logger.info(f"RPC::assign_missing_questions user_id={user_id}")

    # Query for user in db
    user: User = User.query.filter(User.id == user_id).first()

    # Verify they exist
    if user is None:
        logger.error(
            f"RPC::assign_missing_questions user does not exist user_id={user_id}"
        )
        return

    # Get all the courses that the user belongs to
    courses: List[Course] = (
        Course.query.join(InCourse)
        .join(User)
        .filter(
            User.id == user.id,
        )
        .all()
    )

    # Iterate over each course the student is in
    for course in courses:

        # Get all assignments (that have been released and that
        # have not). Skip assignments that have not had their
        # questions assigned yet.
        assignments: List[Assignment] = Assignment.query.filter(
            Assignment.course_id == course.id,
            Assignment.questions_assigned == True,
        ).all()

        # Iterate over assignments
        for assignment in assignments:

            # Run missing question fix for each assignment
            fix_missing_question_assignments(assignment)
