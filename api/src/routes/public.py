from flask import request, redirect, url_for, flash, render_template, Blueprint
from sqlalchemy.exc import IntegrityError
from json import dumps

from ..config import Config
from ..app import db
from ..models import Submissions
from ..utils import enqueue_webhook_job, log_event, get_request_ip

public = Blueprint('public', __name__, url_prefix='/public')


#netids = loads(open('netids.json').read())
netids = {'jmc1283':'jmc1283'}

# dont think we need GET here
@public.route('/webhook', methods=['POST'])
@log_event('job-request', get_request_ip)
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
        if data['before'] == '0000000000000000000000000000000000000000' or data['ref'] != 'refs/heads/master':
            return {'success': False, 'error': ['initial commit or push to master']}

        if not data['repository']['full_name'].startswith('os3224/'):
            return {'success': False, 'error': ['invalid repo']}

        netid=netids[
            data['repository']['name'].split('-')[-1]
        ]
        assignment='-'.join(data['repository']['name'].split('-')[:-1])
        commit=data['after']

        submission=Submissions(
            netid=netid,
            assignment=assignment,
            commit=commit,
            repo=repo_url,
        )

        try:
            db.session.add(submission)
            db.session.commit()
        except IntegrityError as e:
            # TODO handle integ err
            print('Unable to create submission', e)
            return {'success': False}


        enqueue_webhook_job(submission.id)

    return {
        'success': True
    }
