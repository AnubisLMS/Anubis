from flask import request, redirect, url_for, flash, render_template, Blueprint
from sqlalchemy.exc import IntegrityError
from json import dumps

from ..config import Config
from ..app import db
from ..models import Submissions, Student, Assignment
from ..utils import enqueue_webhook_job, log_event, get_request_ip, esindex

public = Blueprint('public', __name__, url_prefix='/public')


def webhook_log_msg():
    if request.headers.get('Content-Type', None) == 'application/json' and \
       request.headers.get('X-GitHub-Event', None) == 'push':
        return request.json['pusher']['name']
    return None

# dont think we need GET here
@public.route('/webhook', methods=['POST'])
@log_event('job-request', webhook_log_msg)
def webhook():
    """
    This route should be hit by the github when a push happens.
    We should take the the github repo url and enqueue it as a job.

    TODO: add per student ratelimiting on this endpoint
    """

    if request.headers.get('Content-Type', None) == 'application/json' and \
       request.headers.get('X-GitHub-Event', None) == 'push':
        data = request.json

        esindex('webhook', data=dumps(data))

        repo_url = data['repository']['ssh_url']
        github_username=data['pusher']['name']
        commit=data['after']
        assignment_name='-'.join(data['repository']['name'].split('-')[:-1])
        assignment=Assignment.query.filter_by(name=assignment_name).first()

        if assignment is None:
            return {'success': False, 'error': ['assignment not found']}

        if data['before'] == '0000000000000000000000000000000000000000' or data['ref'] != 'refs/heads/master':
            return {'success': False, 'error': ['initial commit or push to master']}

        if not data['repository']['full_name'].startswith('os3224/'):
            return {'success': False, 'error': ['invalid repo']}

        submission=Submissions(
            assignment=assignment,
            commit=commit,
            repo=repo_url,
            github_username=github_username,
        )

        student = Student.query.filter_by(
            github_username=github_username,
        ).first()

        if student is not None:
            submission.studentid=student.id

        try:
            db.session.add(submission)
            db.session.commit()
        except IntegrityError as e:
            # TODO handle integ err
            print('Unable to create submission', e)
            return {'success': False}

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
