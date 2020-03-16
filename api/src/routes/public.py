from flask import request, redirect, url_for, flash, render_template, Blueprint, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from json import dumps
from datetime import datetime

from ..config import Config
from ..app import db, cache
from ..models import Submissions, Student, Assignment
from ..utils import enqueue_webhook_job, log_event, get_request_ip, esindex, jsonify, reset_submission

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
@log_event('regrade-request', lambda: 'submission regrade request')
def handle_regrade(commit=None, netid=None):
    """
    This route will get hit whenever someone clicks the regrade button on a
    processed assignment. It should do some validity checks on the commit and
    netid, then reset the submission and re-enqueue the submission job.
    """
    if commit is None or netid is None:
        return jsonify({
            'success': False,
            'error': 'incomplete request',
        })

    student = Student.query.filter_by(netid=netid).first()
    if student is None:
        return jsonify({
            'success': False,
            'errors': 'invalid commit hash or netid'
        })

    submission = Submissions.query.filter_by(
        studentid=student.id,
        commit=commit,
    ).first()

    if submission is None:
        return jsonify({
            'success': False,
            'error': 'invalid commit hash or netid'
        })

    if not submission.processed:
        return jsonify({
            'success': False,
            'error': 'submission currently being processed'
        })

    if not reset_submission(submission):
        return jsonify({
            'success': False,
            'error': 'error regrading'
        })

    enqueue_webhook_job(submission.id)

    return jsonify({
        'success': True
    })


@public.route('/submissions/<commit>/<netid>')
@log_event('submission-request', lambda: 'specifc submission requests')
@cache.cached(timeout=10, key_prefix='web-submission-student')
def handle_submission(commit=None, netid=None):
    if commit is None or netid is None:
        return jsonify({
            'success': False,
            'error': 'missing commit or netid',
        })
    submission = Submissions.query.filter_by(
        commit=commit
    ).first()
    if submission is None:
        return jsonify({
            'success': False,
            'error': 'invalid commit hash or netid',
        })
    if submission.netid != netid:
        return jsonify({
            'success': False,
            'error': 'invalid commit hash or netid'
        })
    return jsonify({
        'data': {
            'submission': submission.json,
            'reports': [r.json for r in submission.reports],
            'tests': submission.tests[0].stdout if len(submission.tests) > 0 else False,
            'build': submission.builds[0].stdout if len(submission.builds) > 0 else False,
            'errors': submission.errors[0].message if len(submission.errors) > 0 else False,
        },
        'success': True
    })

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


        repo_url = data['repository']['ssh_url']
        github_username=data['pusher']['name']
        commit=data['after']
        assignment_name=data['repository']['name'][:-(len(github_username)+1)]
        assignment=Assignment.query.filter_by(name=assignment_name).first()

        if assignment is None:
            return {'success': False, 'error': ['assignment not found']}

        if data['before'] == '0000000000000000000000000000000000000000' or data['ref'] != 'refs/heads/master':
            esindex(
                'new-repo',
                github_username=github_username,
                repo_url=repo_url,
                assignment=str(assignment)
            )
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
            esindex(
                'submission',
                submission=submission.json,
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
