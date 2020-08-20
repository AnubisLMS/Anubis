import logging
import traceback

from flask import request, redirect, Blueprint
from sqlalchemy.exc import IntegrityError

from anubis.models import db, Assignment, Submission, User
from anubis.utils.data import error_response, success_response
from anubis.utils.data import json_response, regrade_submission, enqueue_webhook_job
from anubis.utils.elastic import log_event, esindex

public = Blueprint('public', __name__, url_prefix='/public')


def webhook_log_msg():
    if request.headers.get('Content-Type', None) == 'application/json' and \
    request.headers.get('X-GitHub-Event', None) == 'push':
        return request.json['pusher']['name']
    return None


@public.route('/memes')
@log_event('rick-roll', lambda: 'rick-roll')
def public_memes():
    logging.info('rick-roll')
    return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')


@public.route('/regrade/<commit>')
@log_event('regrade-request', lambda: 'submission regrade request ' + request.path)
@json_response
def public_regrade_commit(commit=None):
    """
    This route will get hit whenever someone clicks the regrade button on a
    processed assignment. It should do some validity checks on the commit and
    netid, then reset the submission and re-enqueue the submission job.
    """
    if commit is None:
        return error_response('incomplete_request'), 406

    # Find the submission
    submission: Submission = Submission.query.filter_by(
        commit=commit
    ).first()

    # Load current user
    student: User = User.current_user()

    # Verify Ownership
    if student is None or submission is None or submission.student_id != student.id:
        return error_response('invalid commit hash or netid'), 406

    # Regrade
    return regrade_submission(submission)


@public.route('/submissions/<commit>')
@log_event('submission-request', lambda: 'specifc submission request ' + request.path)
@json_response
def public_submissions_commit(commit=None):
    if commit is None:
        return error_response('missing commit or netid')
    submission = Submission.query.filter_by(
        commit=commit
    ).first()
    student: User = User.current_user()
    if submission is None:
        return error_response('invalid commit hash or netid')
    if submission.student_id != student.id:
        return error_response('invalid commit hash or netid')

    assignment = submission.assignment

    return success_response({
        'submission': submission.data,
        'assignment': assignment.data,
    })


# dont think we need GET here
@public.route('/webhook', methods=['POST'])
@log_event('job-request', webhook_log_msg)
@json_response
def public_webhook():
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
            return error_response('initial commit or push to master')

        if assignment is None:
            return error_response('assignment not found')

        if not data['repository']['full_name'].startswith('os3224/'):
            return error_response('invalid repo')

        try:
            submission = Submission(
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
            return error_response('unable to commit')

        try:
            student = User.query.filter_by(
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
            return error_response('unable to commit')

        if student is not None:
            submission.student_id = student.id
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
                submission=submission.data,
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
            return error_response('unable to commit')

        # if the github username is not found, create a dangling submission
        if submission.student_id:
            enqueue_webhook_job(submission.id)
        else:
            esindex(
                type='error',
                logs='dangling submission by: ' + submission.github_username,
                submission=submission.id,
                neitd=None,
            )

    return success_response({
        'message': 'webhook successful'
    })

# @public.route('/questions/<str:assignment>')
# @json_response
# def public_questions_assignment(assignment):
#     """
#     This is the route that the frontend will hit to get
#     the questions for a given student. Students will enter
#     their netid and the code that was emailed to them to
#     get their questions. Only with the correct netid and
#     code combination will the request be completed.
#
#     response is json of shape:
#
#     {
#       questions : [
#         {
#           content
#           level
#         },
#         ...
#       ],
#       student: {
#         netid
#         name
#       },
#       success: true
#     }
#
#     or on failure:
#
#     {
#       success: false
#       error: "..."
#     }
#
#     :param netid: netid of student
#     :param code: sha256 hash that was emailed to student
#     :return: json specified above
#     """
#
#     # Mon May 18 2020 09:00:00 GMT-0400 (Eastern Daylight Time)
#     if int(time.time()) <= 1589806800:
#         return error_response('unable to complete request')
#
#     if netid is None or code is None:
#         return error_response('missing fields')
#
#     student = User.query.filter_by(netid=netid).first()
#     if student is None:
#         return error_response('unable to complete request')
#
#     sfq: StudentQuestion = StudentQuestion.query.filter_by(
#         student=student,
#         code=code,
#     ).first()
#     if sfq is None:
#         return error_response('unable to complete request')
#
#     res = sfq.data
#
#     for i in res['questions']:
#         del i['id']
#         del i['solution']
#
#     del res['code']
#     del res['student']['id']
#     del res['student']['github_username']
#
#     return success_response(res)
