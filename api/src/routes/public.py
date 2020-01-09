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
    """

    if request.headers['Content-Type'] == 'application/json':
        received_data = request.json
        repo_url = Config.REPO_SKELETAL + received_data["sender"]["login"]
        enqueue_webhook_job(repo_url)

    return dumps({
        'success': True
    })
