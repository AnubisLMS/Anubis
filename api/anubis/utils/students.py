from parse import parse

from anubis.models import Submission, User, InClass, Class_, Assignment
from anubis.utils.cache import cache
from anubis.utils.data import is_debug
from anubis.utils.http import error_response


@cache.cached(timeout=60 * 60)
def get_students(class_name: str = 'Intro. to Operating Systems'):
    return [s.data for s in User.query.join(InClass).join(Class_).filter(
        Class_.name == class_name,
    ).all()]


@cache.cached(timeout=60 * 60)
def get_students_in_class(class_id):
    return [c.data for c in User.query.join(InClass).join(Class_).filter(
        Class_.id == class_id,
        InClass.owner_id == User.id,
    ).all()]


@cache.memoize(timeout=300, unless=is_debug)
def stats_for(student_id, assignment_id):
    best = None
    best_count = -1
    for submission in Submission.query.filter(
            Submission.assignment_id == assignment_id,
            Submission.owner_id == student_id,
            Submission.processed == True,
    ).order_by(Submission.created.desc()).all():
        correct_count = sum(map(lambda result: 1 if result.passed else 0, submission.test_results))

        if correct_count >= best_count:
            best_count = correct_count
            best = submission
    return best.id if best is not None else None


@cache.memoize(timeout=60 * 60, unless=is_debug)
def bulk_stats(assignment_id, netids=None):
    bests = {}

    assignment = Assignment.query.filter_by(name=assignment_id).first() or Assignment.query.filter_by(
        id=assignment_id).first()
    if assignment is None:
        return error_response('assignment does not exist')

    students = get_students_in_class(assignment.class_id)
    if netids is not None:
        students = filter(
            lambda x: x['netid'] in netids,
            students
        )

    for student in students:
        submission_id = stats_for(student['id'], assignment.id)
        netid = student['netid']
        if submission_id is None:
            # no submission
            bests[netid] = 'No submission'
        else:
            submission = Submission.query.filter(
                Submission.id == submission_id
            ).first()
            repo_path = parse('https://github.com/{}', submission.repo.repo_url)[0]
            best_count = sum(map(lambda x: 1 if x.passed else 0, submission.test_results))
            late = 'past due' if assignment.due_date < submission.created else False
            late = 'past grace' if assignment.grace_date < submission.created else late
            bests[netid] = {
                'submission': submission.data,
                'build': submission.build.stat_data,
                'test_results': [submission_test_result.stat_data for submission_test_result in
                                 submission.test_results],
                'total_tests_passed': best_count,
                'full_stats': 'https://anubis.osiris.services/api/private/submission/{}'.format(submission.id),
                'master': 'https://github.com/{}'.format(repo_path),
                'commits': 'https://github.com/{}/commits/master'.format(repo_path),
                'commit_tree': 'https://github.com/{}/tree/{}'.format(repo_path, submission.commit),
                'late': late
            }

    return bests
