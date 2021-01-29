from parse import parse

from anubis.models import Submission, Assignment
from anubis.utils.cache import cache
from anubis.utils.data import is_debug
from anubis.utils.http import error_response
from anubis.utils.students import get_students_in_class


@cache.memoize(timeout=5 * 60, unless=is_debug)
def stats_for(student_id, assignment_id):
    best = None
    best_count = -1
    for submission in (
        Submission.query.filter(
            Submission.assignment_id == assignment_id,
            Submission.owner_id == student_id,
            Submission.processed,
        )
        .order_by(Submission.created.desc())
        .all()
    ):
        correct_count = sum(
            map(lambda result: 1 if result.passed else 0, submission.test_results)
        )

        if correct_count >= best_count:
            best_count = correct_count
            best = submission
    return best.id if best is not None else None


def stats_wrapper(assignment, user_id, netid, name, submission_id):
    if submission_id is None:
        # no submission
        return {
            "id": netid,
            "user_id": user_id,
            "netid": netid,
            "name": name,
            "submission": None,
            "tests_passed": 0,
            "total_tests": 0,
            "full_stats": None,
            "master": None,
            "commits": None,
            "commit_tree": None,
            "late": False,
        }

    else:
        submission = Submission.query.filter(Submission.id == submission_id).first()
        repo_path = parse("https://github.com/{}", submission.repo.repo_url)[0]
        best_count = sum(map(lambda x: 1 if x.passed else 0, submission.test_results))
        late = "past due" if assignment.due_date < submission.created else "on time"
        late = "past grace" if assignment.grace_date < submission.created else late
        return {
            "id": netid,
            "user_id": user_id,
            "netid": netid,
            "name": name,
            "submission": submission.data,
            "build_passed": submission.build.passed,
            "tests_passed": best_count,
            "total_tests": len(submission.test_results),
            "full_stats": "https://anubis.osiris.services/api/private/submission/{}".format(
                submission.id
            ),
            "master": "https://github.com/{}".format(repo_path),
            "commits": "https://github.com/{}/commits/master".format(repo_path),
            "commit_tree": "https://github.com/{}/tree/{}".format(
                repo_path, submission.commit
            ),
            "late": late,
        }


@cache.memoize(timeout=60 * 60, unless=is_debug)
def bulk_stats(assignment_id, netids=None, offset=0, limit=20):
    bests = []

    assignment = (
        Assignment.query.filter_by(name=assignment_id).first()
        or Assignment.query.filter_by(id=assignment_id).first()
    )
    if assignment is None:
        return error_response("assignment does not exist")

    students = get_students_in_class(assignment.course_id, offset=offset, limit=limit)
    if netids is not None:
        students = filter(lambda x: x["netid"] in netids, students)

    for student in students:
        submission_id = stats_for(student["id"], assignment.id)
        bests.append(
            stats_wrapper(
                assignment,
                student["id"],
                student["netid"],
                student["name"],
                submission_id,
            )
        )

    return bests
