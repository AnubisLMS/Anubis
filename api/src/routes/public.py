from flask import request, redirect, url_for, flash, render_template, Blueprint
from json import dumps

from ..config import Config
from ..app import db
from ..models import Submissions, Results, Events
from ..utils import enqueue_webhook_job, log_event, get_request_ip

public = Blueprint('public', __name__, url_prefix='/public')

# dont think we need GET here
@public.route('/webhook', methods=['POST'])
@log_event('JOB-REQUEST', get_request_ip)
def webhook():
    """
    This route should be hit by the github when a push happens.
    We should take the the github repo url and enqueue it as a job.

    TODO: add checks to validate request
    TODO: pull out assignment name and netid from the request
    TODO: add per student ratelimiting on this endpoint
    """


    if request.headers['Content-Type'] == 'application/json':
        received_data = request.json
        repo_url = Config.REPO_SKELETAL + received_data["sender"]["login"]
        netid='test'
        assignment_name='test'
        enqueue_webhook_job(repo_url, netid, assignment_name)

    return dumps({
        'success': True
    })
