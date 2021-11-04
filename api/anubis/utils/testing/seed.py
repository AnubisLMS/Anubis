import math
import random
import string
import copy
from datetime import datetime, timedelta

from anubis.models import (
    db,
    THEIA_DEFAULT_OPTIONS,
    Assignment,
    AssignmentQuestion,
    AssignmentTest,
    AssignmentRepo,
    Submission,
    User,
    Course,
    InCourse,
    TheiaSession,
)
from anubis.utils.data import rand
from anubis.lms.theia import mark_session_ended
from anubis.utils.github.repos import assignment_repo_name

lorem = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore 
magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""

names = [
    "Joette",
    "Anabelle",
    "Fred",
    "Woodrow",
    "Neoma",
    "Dorian",
    "Treasure",
    "Tami",
    "Berdie",
    "Jordi",
    "Frances",
    "Gerhardt",
    "Kristina",
    "Carmelita",
    "Sim",
    "Hideo",
    "Arland",
    "Wirt",
    "Robt",
    "Narcissus",
    "Steve",
    "Monique",
    "Kellen",
    "Jessenia",
    "Nathalia",
    "Lissie",
    "Loriann",
    "Theresa",
    "Pranav",
    "Eppie",
    "Angelic",
    "Louvenia",
    "Mathews",
    "Natalie",
    "Susan",
    "Cyril",
    "Vester",
    "Rakeem",
    "Duff",
    "Garret",
    "Agnes",
    "Carol",
    "Pairlee",
    "Viridiana",
    "Keith",
    "Elinore",
    "Rico",
    "Demonte",
    "Imelda",
    "Jackeline",
    "Kenneth",
    "Adalynn",
    "Blair",
    "Stetson",
    "Adamaris",
    "Zaniyah",
    "Heyward",
    "Austin",
    "Elden",
    "Gregory",
    "Lemuel",
    "Aaliyah",
    "Abby",
    "Hassie",
    "Sanjuanita",
    "Takisha",
    "Orlo",
    "Geary",
    "Bettye",
    "Luciano",
    "Gretchen",
    "Chimere",
    "Melanie",
    "Angele",
    "Michial",
    "Emmons",
    "Edmund",
    "Renae",
    "Letha",
    "Curtiss",
    "Boris",
    "Winter",
    "Nealy",
    "Renard",
    "Taliyah",
    "Jaren",
    "Nilda",
    "Tiny",
    "Manila",
    "Mariann",
    "Dennis",
    "Autumn",
    "Aron",
    "Drew",
    "Shea",
    "Britt",
    "Luvenia",
    "Doloris",
    "Bret",
    "Sammy",
    "Elmer",
    "Florencio",
    "Selah",
    "Simona",
    "Tatyana",
    "Beau",
    "Alvin",
    "Leslie",
    "Kimberely",
    "Sydni",
    "Mitchel",
    "Belle",
    "Brain",
    "Marlin",
    "Vallie",
    "Colon",
    "Hoyt",
    "Destinee",
    "Shamar",
    "Ezzard",
    "Sheilah",
    "Leisa",
    "Tennille",
    "Brandyn",
    "Yasmin",
    "Malaya",
    "Larry",
    "Mina",
    "Myrle",
    "Blaine",
    "Gusta",
    "Beryl",
    "Abdul",
    "Cleda",
    "Lailah",
    "Alexandrea",
    "Unknown",
    "Gertrude",
    "Davon",
    "Minda",
    "Gabe",
    "Myles",
    "Vonda",
    "Zandra",
    "Salome",
    "Minnie",
    "Merl",
    "Biddie",
    "Catina",
    "Cassidy",
    "Norman",
    "Emilia",
    "Fanny",
    "Nancie",
    "Domingo",
    "Christa",
    "Severt",
    "Danita",
    "Jennie",
    "Anaya",
    "Michelle",
    "Brittnie",
    "Althea",
    "Kimberlee",
    "Ursula",
    "Ballard",
    "Silvester",
    "Ilda",
    "Rock",
    "Tyler",
    "Hildegarde",
    "Aurelio",
    "Lovell",
    "Neha",
    "Jeramiah",
    "Kristin",
    "Kelis",
    "Adolf",
    "Elwood",
    "Almus",
    "Geo",
    "Machelle",
    "Arnulfo",
    "Love",
    "Lollie",
    "Bobbye",
    "Columbus",
    "Susie",
    "Reta",
    "Krysten",
    "Sunny",
    "Alzina",
    "Carolyne",
    "Laurine",
    "Jayla",
    "Halbert",
    "Grayce",
    "Alvie",
    "Haylee",
    "Hosea",
    "Alvira",
    "Pallie",
    "Marylin",
    "Elise",
    "Lidie",
    "Vita",
    "Jakob",
    "Elmira",
    "Oliver",
    "Arra",
    "Debbra",
    "Migdalia",
    "Lucas",
    "Verle",
    "Dellar",
    "Madaline",
    "Iverson",
    "Lorin",
    "Easter",
    "Britta",
    "Kody",
    "Colie",
    "Chaz",
    "Glover",
    "Nickolas",
    "Francisca",
    "Donavan",
    "Merlene",
    "Belia",
    "Laila",
    "Nikhil",
    "Burdette",
    "Mildred",
    "Malissa",
    "Del",
    "Reagan",
    "Loney",
    "Lambert",
    "Ellen",
    "Sydell",
    "Juanita",
    "Alphonsus",
    "Gianna",
    "William",
    "Oneal",
    "Anya",
    "Luis",
    "Shad",
    "Armin",
    "Marvin",
]


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


def create_assignment(
    course,
    users,
    i=0,
    do_submissions=True,
    do_repos=False,
    submission_count=30,
    **kwargs,
):
    release = datetime.now() - timedelta(hours=2)
    due = datetime.now() + timedelta(hours=36) + timedelta(days=i)
    grace = due + timedelta(hours=1)

    # Assignment 1 uniq
    assignment = Assignment(
        id=rand(),
        name=f"{course.course_code} Assignment {i}",
        unique_code=rand(8),
        hidden=False,
        description=lorem,
        github_template="wabscale/xv6-public",
        pipeline_image=f"registry.digitalocean.com/anubis/assignment/{rand(8)}",
        release_date=release,
        due_date=due,
        grace_date=grace,
        course_id=course.id,
        ide_enabled=True,
        autograde_enabled=False,
        theia_options=copy.deepcopy(THEIA_DEFAULT_OPTIONS),
        **kwargs,
    )

    if not do_submissions:
        assignment.theia_options["persistent_storage"] = True

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
        tests.append(
            AssignmentTest(id=rand(), name=f"test {i}", assignment_id=assignment.id)
        )

    submissions = []
    repos = []
    theia_sessions = []
    if do_submissions:
        for user in users:
            repo_name = assignment_repo_name(user, assignment)
            repo_url = f"https://github.com/os3224/{repo_name}"
            if do_repos:
                repo_url = "https://github.com/wabscale/xv6-public"
            repos.append(
                AssignmentRepo(
                    id=rand(),
                    owner=user,
                    assignment_id=assignment.id,
                    repo_url=repo_url,
                    github_username=user.github_username,
                    repo_created=True,
                    collaborator_configured=True,
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
                        id=rand(),
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
    course_id = rand()
    course = Course(id=course_id, join_code=course_id[:6], **kwargs)
    db.session.add(course)

    for user in users:
        db.session.add(InCourse(owner=user, course=course))

    return course


def init_submissions(submissions):
    from anubis.lms.submissions import init_submission

    # Init models
    for submission in submissions:
        init_submission(submission, commit=False)
    db.session.commit()

    for submission in submissions:
        submission.processed = True

        build_pass = random.randint(0, 2) != 0
        submission.build.passed = build_pass
        submission.build.stdout = "blah blah blah build"

        if build_pass:
            for test_result in submission.test_results:
                test_passed = random.randint(0, 3) != 0
                test_result.passed = test_passed

                test_result.message = "Test passed" if test_passed else "Test failed"
                test_result.stdout = "blah blah blah test output"
