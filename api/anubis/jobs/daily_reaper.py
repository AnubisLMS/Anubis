import traceback

from anubis.constants import REAPER_TXT
from anubis.github.team import add_github_team_member, remote_github_team_member, list_github_team_members
from anubis.lms.assignments import get_recent_assignments, verify_active_assignment_github_repo_collaborators
from anubis.lms.courses import get_active_courses, get_course_tas, get_course_professors, get_course_users, user_to_user_id_set
from anubis.lms.questions import fix_missing_question_assignments
from anubis.lms.repos import reap_duplicate_repos
from anubis.models import (
    db,
    Course,
    InCourse,
    User,
)
from anubis.utils.data import with_context
from anubis.utils.logging import logger


def reap_github_admin_teams():
    """
    Make sure tas are properly added to groups

    :return:
    """

    # Get all current courses
    courses: list[Course] = get_active_courses()

    # Iterate through all courses within the system
    for course in courses:
        if course.github_ta_team_slug == '' or course.github_ta_team_slug is None:
            logger.info(f'Skipping reap_github_ta_teams course_id = {course.id}')
            continue

        logger.info(f'Inspecting github ta permissions course_id = {course.id} '
                    f'org = "{course.github_org}" team = "{course.github_ta_team_slug}"')

        # Get all students, professors and TAs for course
        superusers: list[User] = User.query.filter(User.is_superuser == True).all()
        tas: list[User] = get_course_tas(course)
        profs: list[User] = get_course_professors(course)
        members: list[str] = list_github_team_members(course.github_org, course.github_ta_team_slug)

        # Set of members of the team that should be there
        accounted_for_members = set()

        for user in set(tas).union(set(profs)).union(set(superusers)):
            if user.github_username == '' or user.github_username is None:
                logger.info(f'User does not have github linked yet, skipping for now')
                continue

            if user.github_username in members:
                logger.info(f'Skipping adding user to team. Already member user = "{user.id}"')
                accounted_for_members.add(user.github_username)
                continue

            logger.info(f'Adding user to team. Not already member user = "{user.id}"')

            try:
                add_github_team_member(course.github_org, course.github_ta_team_slug, user.github_username)
            except Exception as e:
                logger.error(f'Could not complete member add {e}\n\n' + traceback.format_exc())

            accounted_for_members.add(user.github_username)

        unaccounted_for_members = set(members).difference(accounted_for_members)
        logger.info(f'{members=}\n{accounted_for_members=}')
        logger.info(f'members-accounted_for_members={unaccounted_for_members}')

        # Remove unaccounted for members
        for github_username in unaccounted_for_members:
            remote_github_team_member(course.github_org, course.github_ta_team_slug, github_username)


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

    # Check that course admins are in ta group on GitHub
    reap_github_admin_teams()

    # Make sure all active assignment collaborators are up to date
    verify_active_assignment_github_repo_collaborators()

    # Reap duplicated repo entries
    reap_duplicate_repos()


if __name__ == "__main__":
    print(REAPER_TXT)

    reap()
