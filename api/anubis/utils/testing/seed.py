import copy
import math
import random
import string
import sys
from datetime import datetime, timedelta

from anubis.constants import THEIA_DEFAULT_OPTIONS
from anubis.github.repos import get_student_assignment_repo_name
from anubis.ide.reap import mark_session_ended
from anubis.lms.questions import assign_questions
from anubis.models import (
    ForumPost,
    ForumPostComment,
    ForumCategory,
    ForumPostInCategory,
    ForumPostViewed,
    ForumPostUpvote,
    Assignment,
    AssignmentQuestion,
    AssignmentRepo,
    AssignmentTest,
    Course,
    InCourse,
    ProfessorForCourse,
    Submission,
    TAForCourse,
    TheiaSession,
    TheiaImage,
    TheiaImageTag,
    User,
    Config,
    db,
)
from anubis.models.id import default_id_factory
from anubis.utils.data import rand
from anubis.utils.data import with_context
from anubis.utils.logging import logger
from anubis.utils.testing.db import clear_database
from anubis.utils.testing.diffs import rand_diff
from anubis.utils.testing.lorem import lorem
from anubis.utils.testing.names import names


def create_name() -> str:
    """
    Get a randomly generated first and last
    name from the list of names.

    :return:
    """
    return f"{random.choice(names)} {random.choice(names)}"


def create_netid(name: str) -> str:
    """
    Generate a netid from a provided name. This will
    pull the initials from the name and append some
    numbers.

    :param name:
    :return:
    """
    initials = "".join(word[0].lower() for word in name.split())
    numbers = "".join(random.choice(string.digits) for _ in range(3))

    return f"{initials}{numbers}"


def rand_commit(n=40) -> str:
    """
    Generate a random commit hash. The commit length will
    be 40 characters.

    :param n:
    :return:
    """
    from anubis.utils.data import rand

    return rand(n)


def init_forums(course: Course):
    student1 = User.query.join(InCourse).join(Course).filter(Course.id == course.id).first()
    student2 = User.query.join(InCourse).join(Course).filter(Course.id == course.id).offset(1).first()
    for i in range(3):
        post = ForumPost(
            owner_id=student1.id,
            course_id=course.id,
            visible_to_students=True,
            pinned=False,
            anonymous=False,
            title=f'POST POST POST {course.course_code}',
            content={
                'blocks':        [{
                    'key':          '4f5r7',
                    'text':         f'POST POST POST {course.course_code}',
                    'type':         'unstyled',
                    'depth':        0, 'inlineStyleRanges': [{'offset': 9, 'length': 8, 'style': 'BOLD'}],
                    'entityRanges': [], 'data': {},
                }], 'entityMap': {},
            },
        )
        db.session.add(post)

        category = ForumCategory(
            name=f"Category {i}",
            course=course,
        )
        db.session.add(category)

        in_category = ForumPostInCategory(
            post=post,
            category=category,
        )
        db.session.add(in_category)

        upvote = ForumPostUpvote(owner=student2, post=post)
        db.session.add(upvote)

        viewed1 = ForumPostViewed(owner=student1, post=post)
        viewed2 = ForumPostViewed(owner=student2, post=post)
        db.session.add_all([viewed1, viewed2])

        comments: list[ForumPostComment] = []
        for k in range(3):
            parent_id = default_id_factory()
            comment0 = ForumPostComment(
                id=parent_id, owner_id=student1.id, post=post,
                parent_id=None, approved_by_id=None, anonymous=False, thread_start=True,
                content={
                    'blocks':    [{
                        'key':               '4f5r7',
                        'text':              f'COMMENT {k} 0',
                        'type':              'unstyled',
                        'depth':             0,
                        'inlineStyleRanges': [{
                            'offset': 9,
                            'length': 8,
                            'style':  'BOLD'}],
                        'entityRanges':      [],
                        'data':              {},
                    }],
                    'entityMap': {},
                }
            )
            comment1 = ForumPostComment(
                id=default_id_factory(), owner_id=student2.id, post=post,
                parent_id=parent_id, approved_by_id=None, anonymous=False, thread_start=False,
                content={
                    'blocks':    [{
                        'key':               '4f5r7',
                        'text':              f'COMMENT {k} 1',
                        'type':              'unstyled',
                        'depth':             0,
                        'inlineStyleRanges': [{
                            'offset': 9,
                            'length': 8,
                            'style':  'BOLD'}],
                        'entityRanges':      [],
                        'data':              {},
                    }],
                    'entityMap': {},
                }
            )
            comments.append(comment0)
            comments.append(comment1)
        db.session.add_all(comments)


def create_assignment(
    course,
    users,
    xv6_image,
    i=0,
    do_submissions=True,
    do_repos=False,
    submission_count=5,
    **kwargs,
):
    logger.info(f'creating {course.name} assignment {i}')
    release = datetime.now() - timedelta(hours=2)
    due = datetime.now() + timedelta(hours=36) + timedelta(days=i)
    grace = due + timedelta(hours=1)

    # Assignment 1 uniq
    assignment = Assignment(
        id=default_id_factory(),
        name=f"{course.course_code} Assignment {i}",
        unique_code=rand(8),
        hidden=False,
        description=lorem,
        github_template="AnubisLMS/xv6",
        pipeline_image=f"registry.digitalocean.com/anubis/assignment/{rand(8)}",
        release_date=release,
        due_date=due,
        grace_date=grace,
        course_id=course.id,
        ide_enabled=True,
        autograde_enabled=False,
        theia_options=copy.deepcopy(THEIA_DEFAULT_OPTIONS),
        theia_image_id=xv6_image.id,
        **kwargs,
    )

    if not do_submissions:
        assignment.theia_options["persistent_storage"] = True

    for i in range(random.randint(2, 4)):
        b, c = random.randint(1, 5), random.randint(1, 5)
        assignment_question = AssignmentQuestion(
            id=default_id_factory(),
            question=f"What is {c} + {b}?",
            solution=f"{c + b}",
            pool=i,
            code_question=False,
            assignment_id=assignment.id,
        )
        db.session.add(assignment_question)

    tests = []

    if not kwargs.get('shell_autograde_enabled', False):
        n = 0
        for i in range(random.randint(3, 5)):
            tests.append(
                AssignmentTest(id=default_id_factory(), name=f"test {i}", assignment_id=assignment.id, order=n))
            n += 1
    else:
        tests = [
            AssignmentTest(id=default_id_factory(), name='helloworld', assignment_id=assignment.id, order=0),
            AssignmentTest(id=default_id_factory(), name='mkdir exercise1', assignment_id=assignment.id, order=1),
            AssignmentTest(id=default_id_factory(), name='cd exercise1', assignment_id=assignment.id, order=2),
            AssignmentTest(id=default_id_factory(), name='pipe hello world', assignment_id=assignment.id, order=3),
        ]

    submissions = []
    repos = []
    theia_sessions = []
    if do_submissions:
        for user in users:
            repo_name = get_student_assignment_repo_name(user, assignment)
            repo_url = f"https://github.com/os3224/{repo_name}"
            if do_repos:
                repo_url = "https://github.com/AnubisLMS/xv6"
            repos.append(
                AssignmentRepo(
                    id=default_id_factory(),
                    owner=user,
                    assignment_id=assignment.id,
                    repo_url=repo_url,
                    netid=user.netid,
                    repo_created=True,
                    collaborator_configured=True,
                    ta_configured=True,
                )
            )

            for _ in range(3):
                theia_session = TheiaSession(
                    owner=user,
                    assignment=assignment,
                    course=course,
                    repo_url=repos[-1].repo_url,
                    cluster_address="127.0.0.1",
                )
                mark_session_ended(theia_session)
                theia_sessions.append(theia_session)

            if submission_count is not None:
                for i in range(submission_count):
                    submission = Submission(
                        id=default_id_factory(),
                        commit=rand_commit(),
                        state="Waiting for resources...",
                        owner=user,
                        assignment_id=assignment.id,
                        created=grace - timedelta(hours=math.sqrt(i + 1)),
                    )
                    submission.repo = repos[-1]
                    submissions.append(submission)

        db.session.add_all(submissions)
        db.session.add_all(theia_sessions)
        db.session.add_all(repos)
    db.session.add_all(tests)
    db.session.add(assignment)

    return assignment, tests, submissions, repos


def create_students(n=10) -> list[User]:
    students = []
    netids = set()
    while len(students) < n:

        # Make random name + netid
        name = create_name()
        netid = create_netid(name)

        # If netid is already in list of students, then
        # continue to make a new one. Netid's need to be
        # unique or it causes problems
        if netid in netids:
            continue
        netids.add(netid)

        # Add student to list
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
    course_id = default_id_factory()
    course = Course(id=course_id, join_code=kwargs['name'].lower().replace(' ', '_'), **kwargs)
    db.session.add(course)

    for user in users:
        db.session.add(InCourse(owner=user, course=course))

    return course


def init_submissions(submissions):
    from anubis.lms.submissions import init_submission

    # Init models
    for submission in submissions:
        init_submission(submission, db_commit=False, verbose=False)
    db.session.commit()

    for submission in submissions:
        submission.processed = True
        submission.pipeline_log = "blah blah blah log"

        build_pass = random.randint(0, 2) != 0
        submission.build.passed = build_pass
        submission.build.stdout = "blah blah blah build"

        if build_pass:
            for test_result in submission.test_results:
                test_passed = random.randint(0, 1) != 0
                test_result.passed = test_passed

                if test_passed:
                    test_result.message = "Test passed"
                    test_result.output_type = "text"
                    test_result.output = "Test passed"
                else:
                    test_result.message = "Test failed"
                    test_result.output_type = "diff"
                    test_result.output = rand_diff()


@with_context
def seed():
    logger.info('clearing db')
    clear_database()

    # Create
    logger.info('creating top level users')
    superuser = User(netid="superuser", github_username="superuser", name="super", is_superuser=True)
    ta_user = User(netid="ta", github_username="ta", name="T A")
    professor_user = User(netid="professor", github_username="professor", name="professor")
    student_user = User(netid="student", github_username="student", name="student")
    db.session.add_all([superuser, professor_user, ta_user, student_user])

    logger.info('creating theia image + tags')
    base_image = TheiaImage(
        image="registry.digitalocean.com/anubis/theia-base",
        title="Python IDE",
        description="Python IDE",
        icon="devicon-python-plain",
        default_tag="python-3.10",
        public=True,
    )
    base_tag38 = TheiaImageTag(
        tag="python-3.8",
        title="Python 3.8",
        description="Python IDE",
        image=base_image,
    )
    base_tag39 = TheiaImageTag(
        tag="python-3.9",
        title="Python 3.9",
        description="Python IDE",
        image=base_image,
    )
    base_tag310 = TheiaImageTag(
        tag="python-3.10",
        title="Python 3.10",
        description="Python IDE",
        image=base_image,
    )
    db.session.add_all([base_tag38, base_tag39, base_tag310])

    xv6_image = TheiaImage(
        image="registry.digitalocean.com/anubis/theia-cpp",
        title="C/C++ IDE",
        description="C/C++ IDE",
        icon="devicon-cplusplus-plain",
        public=True,
    )
    admin_image = TheiaImage(
        image="registry.digitalocean.com/anubis/theia-admin",
        title="theia-admin",
        description="Admin IDE",
        icon="devicon-python-plain",
        public=False,
    )
    db.session.add_all([xv6_image, base_image, admin_image])

    base_webtop = TheiaImage(
        image="registry.digitalocean.com/anubis/webtop-base",
        title="Webtop Base",
        description="Webtop Base",
        icon="devicon-linux-plain",
        default_tag="ubuntu",
        public=True,
        webtop=True,
    )
    db.session.add_all([base_webtop])

    db.session.commit()

    # OS test course
    logger.info('creating os students')
    intro_to_os_students = create_students(10) + [
        superuser,
        professor_user,
        ta_user,
        student_user,
    ]
    logger.info('creating os course')
    intro_to_os_course = create_course(
        intro_to_os_students,
        name="Intro to OS",
        course_code="CS-UY 3224",
        section="A",
        professor_display_name="Gustavo",
        autograde_tests_repo="https://github.com/os3224/anubis-assignment-tests",
        github_org="os3224",
    )

    logger.info('creating forum for os')

    os_assignment0, _, os_submissions0, _ = create_assignment(
        intro_to_os_course,
        intro_to_os_students,
        xv6_image,
        i=0,
        github_repo_required=True,
    )
    os_assignment1, _, os_submissions1, _ = create_assignment(
        intro_to_os_course,
        intro_to_os_students,
        xv6_image,
        i=1,
        do_submissions=False,
        github_repo_required=True,
    )
    os_assignment2, _, os_submissions2, _ = create_assignment(
        intro_to_os_course,
        intro_to_os_students,
        xv6_image,
        i=2,
        do_submissions=False,
        github_repo_required=False,
    )
    os_assignment3, _, os_submissions3, _ = create_assignment(
        intro_to_os_course,
        intro_to_os_students,
        xv6_image,
        i=3,
        do_submissions=True,
        do_repos=True,
        github_repo_required=True,
    )
    os_assignment4, _, _, _ = create_assignment(
        intro_to_os_course,
        intro_to_os_students,
        xv6_image,
        i=4,
        do_submissions=False,
        do_repos=False,
        github_repo_required=False,
        shell_autograde_enabled=True,
        shell_autograde_repo='jepst/BashExercises1122',
        shell_autograde_exercise_path='sample/exercise.py',
    )
    os_assignment4.theia_options['autosave'] = False
    os_assignment4.theia_options['persistent_storage'] = False
    os_assignment4.theia_options['network_policy'] = 'shell-autograde-student'
    os_assignment4.theia_options['network_dns_locked'] = False
    logger.info('init submissions assignment 0')
    init_submissions(os_submissions0)
    assign_questions(os_assignment0)
    logger.info('init submissions assignment 1')
    init_submissions(os_submissions1)
    assign_questions(os_assignment1)
    logger.info('init submissions assignment 2')
    init_submissions(os_submissions2)
    assign_questions(os_assignment2)
    logger.info('init submissions assignment 3')
    init_submissions(os_submissions3)
    assign_questions(os_assignment3)
    assign_questions(os_assignment4)
    init_forums(intro_to_os_course)

    logger.info('adding course tas + profs')
    ta = TAForCourse(owner=ta_user, course=intro_to_os_course)
    professor = ProfessorForCourse(owner=professor_user, course=intro_to_os_course)
    db.session.add_all([professor, ta])

    # MMDS test course
    logger.info('creating mmds student')
    mmds_students = create_students(10)

    logger.info('adding mmds course')
    mmds_course = create_course(
        mmds_students,
        name="Mining Massive Datasets",
        course_code="CS-UY 3843",
        section="A",
        professor_display_name="Gustavo",
        autograde_tests_repo="https://github.com/os3224/anubis-assignment-tests",
        github_org="os3224",
    )
    mmds_assignment, _, mmds_submissions, _ = create_assignment(mmds_course, mmds_students, xv6_image)

    logger.info('init mmds submissions')
    init_submissions(mmds_submissions)
    assign_questions(mmds_assignment)

    playground_dockerd_config = Config.query.filter_by(key='PLAYGROUND_DOCKERD')
    if playground_dockerd_config is None:
        playground_dockerd_config = Config(key='PLAYGROUND_DOCKERD', value='ON')
        db.session.add(playground_dockerd_config)

    admin = Config(key='ADMIN_NETID', value='superuser')
    db.session.add(admin)

    logger.info('committing')
    db.session.commit()
    init_forums(intro_to_os_course)
    init_forums(mmds_course)
    db.session.commit()
