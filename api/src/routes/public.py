import traceback

from flask import request, redirect, Blueprint
from sqlalchemy.exc import IntegrityError

from ..app import db, cache
from ..models import Submissions, Student, Assignment, StudentFinalQuestions
from ..utils import enqueue_webhook_job, log_event, esindex, regrade_submission, json

public = Blueprint('public', __name__, url_prefix='/public')


def webhook_log_msg():
    if request.headers.get('Content-Type', None) == 'application/json' and \
            request.headers.get('X-GitHub-Event', None) == 'push':
        return request.json['pusher']['name']
    return None


@public.route('/memes')
@log_event('rick-roll', lambda: 'rick-roll')
def handle_memes():
    return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')


@public.route('/regrade/<commit>/<netid>')
@log_event('regrade-request', lambda: 'submission regrade request ' + request.path)
@json
def handle_regrade(commit=None, netid=None):
    """
    This route will get hit whenever someone clicks the regrade button on a
    processed assignment. It should do some validity checks on the commit and
    netid, then reset the submission and re-enqueue the submission job.
    """
    if commit is None or netid is None:
        return {
            'success': False,
            'error': 'incomplete request',
        }

    student = Student.query.filter_by(netid=netid).first()
    if student is None:
        return {
            'success': False,
            'errors': 'invalid commit hash or netid'
        }

    submission = Submissions.query.filter_by(
        studentid=student.id,
        commit=commit,
    ).first()

    if submission is None:
        return {
            'success': False,
            'error': 'invalid commit hash or netid'
        }

    return regrade_submission(submission)


@public.route('/submissions/<commit>/<netid>')
@log_event('submission-request', lambda: 'specifc submission request ' + request.path)
@cache.memoize(timeout=2)
@json
def handle_submission(commit=None, netid=None):
    if commit is None or netid is None:
        return {
            'success': False,
            'error': 'missing commit or netid',
        }
    submission = Submissions.query.filter_by(
        commit=commit
    ).first()
    if submission is None:
        return {
            'success': False,
            'error': 'invalid commit hash or netid',
        }
    if submission.netid != netid:
        return {
            'success': False,
            'error': 'invalid commit hash or netid'
        }

    return {
        'data': {
            'submission': submission.json,
            'reports': [r.json for r in submission.reports],
            'tests': submission.tests[0].stdout if len(submission.tests) > 0 else False,
            'build': submission.builds[0].stdout if len(submission.builds) > 0 else False,
            'errors': submission.errors[0].message if len(submission.errors) > 0 else False,
        },
        'success': True
    }


# dont think we need GET here
@public.route('/webhook', methods=['POST'])
@log_event('job-request', webhook_log_msg)
@json
def webhook():
    """
    This route should be hit by the github when a push happens.
    We should take the the github repo url and enqueue it as a job.
    """

    if request.headers.get('Content-Type', None) == 'application/json' and \
            request.headers.get('X-GitHub-Event', None) == 'push':
        data = request.json

        repo_url = data['repository']['ssh_url']
        github_username = data['pusher']['name']
        commit = data['after']
        assignment_name = data['repository']['name'][:-(len(github_username) + 1)]
        assignment = Assignment.query.filter_by(name=assignment_name).first()

        if data['before'] == '0000000000000000000000000000000000000000' or data['ref'] != 'refs/heads/master':
            esindex(
                'new-repo',
                github_username=github_username,
                repo_url=repo_url,
                assignment=str(assignment)
            )
            return {'success': False, 'error': ['initial commit or push to master']}

        if assignment is None:
            return {'success': False, 'error': ['assignment not found']}

        if not data['repository']['full_name'].startswith('os3224/'):
            return {'success': False, 'error': ['invalid repo']}

        try:
            submission = Submissions(
                assignment=assignment,
                commit=commit,
                repo=repo_url,
                github_username=github_username,
            )
        except IntegrityError as e:
            tb = traceback.format_exc()
            esindex(
                'error',
                type='webhook',
                logs=tb,
                submission=None,
                netid=None,
            )
            return {'success': False, 'error': ['integrity error']}

        try:
            student = Student.query.filter_by(
                github_username=github_username,
            ).first()
        except IntegrityError as e:
            tb = traceback.format_exc()
            esindex(
                'error',
                type='webhook',
                logs=tb,
                submission=None,
                netid=None,
            )
            return {'success': False, 'error': ['integrity error']}

        if student is not None:
            submission.studentid = student.id
            esindex(
                index='submission',
                processed=0,
                error=-1,
                passed=-1,
                netid=submission.netid,
                commit=submission.commit,
                assignment=submission.assignment.name,
                report=submission.url,
            )
        else:
            esindex(
                'dangling',
                submission=submission.json,
            )

        try:
            db.session.add(submission)
            db.session.commit()
        except IntegrityError as e:
            tb = traceback.format_exc()
            esindex(
                'error',
                type='webhook',
                logs=tb,
                submission=None,
                netid=None,
            )
            return {'success': False, 'errors': ['integrity error']}

        # if the github username is not found, create a dangling submission
        if submission.studentid:
            enqueue_webhook_job(submission.id)
        else:
            esindex(
                type='error',
                logs='dangling submission by: ' + submission.github_username,
                submission=submission.id,
                neitd=None,
            )

    return {
        'success': True
    }


@public.route('/finalquestions/<netid>/<code>')
@json
def pub_finalquestions(netid, code):
    """
    This is the route that the frontend will hit to get
    the questions for a given student. Students will enter
    their netid and the code that was emailed to them to
    get their questions. Only with the correct netid and
    code combination will the request be completed.

    response is json of shape:

    {
      questions : [
        {
          content
          level
        },
        ...
      ],
      student: {
        netid
        name
      },
      success: true
    }

    or on failure:

    {
      success: false
      error: "..."
    }

    :param netid: netid of student
    :param code: sha256 hash that was emailed to student
    :return: json specified above
    """
    unable_to_complete = {
        'success': False,
        'error': 'unable to complete request'
    }

    if netid is None or code is None:
        return {
            'success': False,
            'error': 'missing fields'
        }

    student = Student.query.filter_by(netid=netid).first()
    if student is None:
        return unable_to_complete

    sfq = StudentFinalQuestions.query.filter_by(
        student=student,
        code=code,
    ).first()
    if sfq is None:
        return unable_to_complete

    res = sfq.json

    for i in res['questions']:
        del i['id']
        del i['solution']

    del res['code']
    del res['student']['id']
    del res['student']['github_username']

    res['success'] = True

    return res

