import time

from anubis.lms.autograde import bulk_autograde
from anubis.models import db
from anubis.utils.data import with_context
from anubis.utils.testing.db import clear_database
from anubis.utils.testing.seed import create_assignment, create_course, create_students, init_submissions


def do_seed() -> str:
    clear_database()

    # OS test course
    intro_to_os_students = create_students(100)
    intro_to_os_course = create_course(
        intro_to_os_students,
        name="Intro to OS",
        course_code="CS-UY 3224",
        section="A",
        professor_display_name="Gustavo",
        autograde_tests_repo="https://github.com/os3224/anubis-assignment-tests",
        github_org="os3224",
    )
    os_assignment0, _, os_submissions0, _ = create_assignment(
        intro_to_os_course,
        intro_to_os_students,
        i=0,
        github_repo_required=True,
        submission_count=50,
    )
    init_submissions(os_submissions0)

    db.session.commit()

    return os_assignment0.id


@with_context
def main():
    print("Seeding submission data")
    seed_start = time.time()
    assignment_id = do_seed()
    seed_end = time.time()
    print("Seed done in {}s".format(seed_end - seed_start))

    n = 10
    timings = []
    print(f"Running bulk autograde on assignment {n} times [ 5K submissions, across 50 students ]")
    for i in range(n):
        print(f"autograde pass {i + 1}/{n} ", end="", flush=True)
        db.session.expunge_all()
        start = time.time()
        bulk_autograde(assignment_id, limit=100)
        end = time.time()
        timings.append(end - start)

        print("{:.2f}s".format(end - start))

    print("Average time :: {:.2f}s".format(sum(timings) / len(timings)))


if __name__ == "__main__":
    main()
