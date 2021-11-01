from anubis.models import (
    db,
    SubmissionTestResult,
    SubmissionBuild,
    Submission,
    AssignmentRepo,
    AssignmentTest,
    InCourse,
    Assignment,
    Course,
    User,
    TheiaSession,
    AssignmentQuestion,
    AssignedStudentQuestion,
    AssignedQuestionResponse,
    TAForCourse,
    ProfessorForCourse,
    StaticFile,
    LateException,
    LectureNotes,
)
from anubis.utils.data import with_context
from anubis.lms.questions import assign_questions
from anubis.utils.testing.seed import (
    create_assignment,
    create_students,
    create_course,
    init_submissions,
)


@with_context
def seed():
    # Yeet
    LateException.query.delete()
    TheiaSession.query.delete()
    AssignedQuestionResponse.query.delete()
    AssignedStudentQuestion.query.delete()
    AssignmentQuestion.query.delete()
    SubmissionTestResult.query.delete()
    SubmissionBuild.query.delete()
    Submission.query.delete()
    AssignmentRepo.query.delete()
    AssignmentTest.query.delete()
    InCourse.query.delete()
    Assignment.query.delete()
    TAForCourse.query.delete()
    ProfessorForCourse.query.delete()
    LectureNotes.query.delete()
    StaticFile.query.delete()
    Course.query.delete()
    User.query.delete()
    db.session.commit()

    # Create
    superuser = User(netid="superuser", github_username="superuser", name="super", is_superuser=True)
    ta_user = User(netid="ta", github_username="ta", name="T A")
    professor_user = User(netid="professor", github_username="professor", name="professor")
    student_user = User(netid="student", github_username="student", name="student")
    db.session.add_all([superuser, professor_user, ta_user, student_user])

    # OS test course
    intro_to_os_students = create_students(50) + [superuser, professor_user, ta_user, student_user]
    intro_to_os_course = create_course(
        intro_to_os_students,
        name="Intro to OS", course_code="CS-UY 3224", section="A", professor_display_name="Gustavo",
        autograde_tests_repo='https://github.com/os3224/anubis-assignment-tests',
        github_org='os3224',
    )
    ta = TAForCourse(owner=ta_user, course=intro_to_os_course)
    professor = ProfessorForCourse(owner=professor_user, course=intro_to_os_course)
    db.session.add_all([professor, ta])
    db.session.commit()

    os_assignment0, _, os_submissions0, _ = create_assignment(
        intro_to_os_course, intro_to_os_students, i=0, github_repo_required=True,
    )
    os_assignment1, _, os_submissions1, _ = create_assignment(
        intro_to_os_course, intro_to_os_students, i=1, do_submissions=False, github_repo_required=True,
    )
    os_assignment2, _, os_submissions2, _ = create_assignment(
        intro_to_os_course, intro_to_os_students, i=2, do_submissions=False, github_repo_required=False,
    )
    os_assignment3, _, os_submissions3, _ = create_assignment(
        intro_to_os_course, intro_to_os_students, i=3, do_submissions=True, do_repos=True, github_repo_required=True,
    )
    init_submissions(os_submissions0)
    assign_questions(os_assignment0)
    init_submissions(os_submissions1)
    assign_questions(os_assignment1)
    init_submissions(os_submissions2)
    assign_questions(os_assignment2)
    init_submissions(os_submissions3)
    assign_questions(os_assignment3)

    # MMDS test course
    mmds_students = create_students(50)
    mmds_course = create_course(
        mmds_students,
        name="Mining Massive Datasets", course_code="CS-UY 3843", section="A", professor_display_name="Gustavo",
        autograde_tests_repo='https://github.com/os3224/anubis-assignment-tests',
        github_org='os3224'
    )
    mmds_assignment, _, mmds_submissions, _ = create_assignment(mmds_course, mmds_students)
    init_submissions(mmds_submissions)
    assign_questions(mmds_assignment)

    db.session.commit()
