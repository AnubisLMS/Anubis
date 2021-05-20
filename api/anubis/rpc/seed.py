import random
from datetime import datetime, timedelta

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
)
from anubis.utils.data import rand, with_context
from anubis.utils.lms.questions import assign_questions
from anubis.utils.seed import create_name, create_netid, rand_commit


def create_assignment(course, users):
    # Assignment 1 uniq
    assignment = Assignment(
        id=rand(), name=f"assignment {course.name}", unique_code=rand(8), hidden=False,
        pipeline_image=f"registry.osiris.services/anubis/assignment/{rand(8)}",
        github_classroom_url='http://localhost',
        release_date=datetime.now() - timedelta(hours=2),
        due_date=datetime.now() + timedelta(hours=12),
        grace_date=datetime.now() + timedelta(hours=13),
        course_id=course.id, ide_enabled=True, autograde_enabled=False,
    )

    for i in range(random.randint(2, 4)):
        b, c = random.randint(1, 5), random.randint(1, 5)
        assignment_question = AssignmentQuestion(
            id=rand(),
            question=f"What is {c} + {b}?",
            solution=f"{c + b}",
            pool=i,
            code_question=False,
            assignment_id=assignment.id,
        )
        db.session.add(assignment_question)

    tests = []
    for i in range(random.randint(3, 5)):
        tests.append(AssignmentTest(id=rand(), name=f"test {i}", assignment_id=assignment.id))

    submissions = []
    repos = []
    theia_sessions = []
    for user in users:
        repos.append(
            AssignmentRepo(
                id=rand(), owner=user, assignment_id=assignment.id,
                repo_url="https://github.com/wabscale/xv6-public",
                github_username=user.github_username,
            )
        )

        # for _ in range(2):
        #     theia_sessions.append(
        #         TheiaSession(
        #             owner=user,
        #             assignment=assignment,
        #             repo_url=repos[-1].repo_url,
        #             active=False,
        #             ended=datetime.now(),
        #             state="state",
        #             cluster_address="127.0.0.1",
        #         )
        #     )
        # theia_sessions.append(
        #     TheiaSession(
        #         owner=user,
        #         assignment=assignment,
        #         repo_url=repos[-1].repo_url,
        #         active=True,
        #         state="state",
        #         cluster_address="127.0.0.1",
        #     )
        # )

        if random.randint(0, 3) != 0:
            for i in range(random.randint(1, 10)):
                submissions.append(
                    Submission(
                        id=rand(),
                        commit=rand_commit(),
                        state="Waiting for resources...",
                        owner=user,
                        assignment_id=assignment.id,
                        repo=repos[-1],
                    )
                )

    db.session.add_all(tests)
    db.session.add_all(submissions)
    db.session.add_all(theia_sessions)
    db.session.add_all(repos)
    db.session.add(assignment)

    return assignment, tests, submissions, repos


def create_students(n=10):
    students = []
    for i in range(random.randint(n // 2, n)):
        name = create_name()
        netid = create_netid(name)
        students.append(
            User(
                name=name,
                netid=netid,
                github_username=rand(8),
                is_superuser=False,
            )
        )
    db.session.add_all(students)
    return students


def create_course(users, **kwargs):
    course = Course(id=rand(), **kwargs)
    db.session.add(course)

    for user in users:
        db.session.add(InCourse(owner=user, course=course))

    return course


def init_submissions(submissions):
    # Init models
    for submission in submissions:
        submission.init_submission_models()
        submission.processed = True

        build_pass = random.randint(0, 2) != 0
        submission.build.passed = build_pass
        submission.build.stdout = 'blah blah blah build'

        if build_pass:
            for test_result in submission.test_results:
                test_passed = random.randint(0, 3) != 0
                test_result.passed = test_passed

                test_result.message = 'Test passed' if test_passed else 'Test failed'
                test_result.stdout = 'blah blah blah test output'


@with_context
def seed():
    # Yeet
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
        name="Intro to OS", course_code="CS-UY 3224", section="A", professor="Gustavo",
    )
    os_assignment, _, os_submissions, _ = create_assignment(intro_to_os_course, intro_to_os_students)
    init_submissions(os_submissions)
    assign_questions(os_assignment)
    ta = TAForCourse(owner=ta_user, course=intro_to_os_course)
    professor = ProfessorForCourse(owner=professor_user, course=intro_to_os_course)
    db.session.add_all([professor, ta])

    # MMDS test course
    mmds_students = create_students(50)
    mmds_course = create_course(
        mmds_students,
        name="Mining Massive Datasets", course_code="CS-UY 3843", section="A", professor="Gustavo",
    )
    mmds_assignment, _, mmds_submissions, _ = create_assignment(mmds_course, mmds_students)
    init_submissions(mmds_submissions)
    assign_questions(mmds_assignment)

    db.session.commit()
