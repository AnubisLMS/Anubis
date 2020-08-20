import logging
import traceback

from flask import request, redirect, Blueprint
from sqlalchemy.exc import IntegrityError

from anubis.models import db, Assignment, Submission, User
from anubis.utils.auth import current_user
from anubis.utils.data import error_response, success_response
from anubis.utils.data import json_response, regrade_submission, enqueue_webhook_rpc
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
    user: User = User.current_user()

    # Verify Ownership
    if user is None or submission is None or submission.owner.id != user.id:
        return error_response('invalid commit hash or netid'), 406

    # Regrade
    return regrade_submission(submission)


@public.route('/submission/<commit>')
@log_event('submission-request', lambda: 'specifc submission request ' + request.path)
@json_response
def public_submission_commit(commit):
    """
    This endpoint is hit by the frontend when a user clicks on a specific
    submission. It should provide the basic information about that submission.

    :param commit:
    :return:
    """
    # Verify Commit
    submission = Submission.query.filter_by(commit=commit).first()
    if submission is None:
        return error_response('invalid commit hash or netid'), 406

    # Verify Ownership
    user: User = User.current_user()
    if submission.owner.id != user.id:
        return error_response('invalid commit hash or netid'), 406

    # Get the assignment
    assignment = submission.assignment

    # Return the basic data
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

    content_type = request.headers.get('Content-Type', None)
    x_github_event = request.headers.get('X-GitHub-Event', None)

    # Verify some expected headers
    if not (content_type == 'application/json' and x_github_event == 'push'):
        return error_response('Unable to verify webhook')

    webhook = request.json

    # Load the basics from the webhook
    repo_url = webhook['repository']['ssh_url']
    github_username = webhook['pusher']['name']
    commit = webhook['after']
    assignment_name = webhook['repository']['name'][:-(len(github_username) + 1)]
    assignment = Assignment.query.filter_by(name=assignment_name).first()

    # Verify that we can match this push to an assignment
    if assignment is None:
        esindex(
            'error',
            github_username=github_username,
            repo_url=repo_url,
            assignment_name=assignment_name
        )
        return error_response('assignment not found')

    # The before Hash will be all 0s on for the first hash.
    # We will want to ignore both this first push (the initialization of the repo)
    # and all branches that are not master.
    if webhook['before'] == '0000000000000000000000000000000000000000' or webhook['ref'] != 'refs/heads/master':
        # Record that a new repo was created (and therefore, someone just started their assignment)
        esindex(
            'new-repo',
            github_username=github_username,
            repo_url=repo_url,
            assignment=str(assignment)
        )
        return success_response('initial commit or push to master')

    # Make sure that the repo we're about to process actually belongs to our organization
    if not webhook['repository']['full_name'].startswith('os3224/'):
        return error_response('invalid repo')

    # Create a shiny new submission
    submission = Submission(
        assignment=assignment,
        commit=commit,
        repo=repo_url,
        github_username=github_username,
    )

    # Commit submission
    try:
        db.session.add(submission)
        db.session.commit()
    except IntegrityError:
        tb = traceback.format_exc()
        esindex('error', type='webhook', logs=tb, submission=submission, netid=None, )
        return error_response('unable to commit'), 400

    # Match the github username in the webhook to
    # a user in the database (hopefully)
    user = User.query.filter_by(
        github_username=github_username,
    ).first()

    # If a user has not given us their github username
    # the submission will stay in a "dangling" state
    if user is None:
        esindex(
            type='error',
            logs='dangling submission by: ' + submission.github_username,
            submission=submission.id,
            neitd=None,
        )
        return error_response('dangling submission')

    # Associate the submission with the user
    submission.student_id = user.id

    # Log the submission
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

    # Update the submission with the user information
    try:
        db.session.add(submission)
        db.session.commit()
    except IntegrityError:
        tb = traceback.format_exc()
        esindex('error', type='webhook', logs=tb, submission=submission, netid=None)
        return error_response('unable to commit'), 400

    # if the github username is not found, create a dangling submission
    enqueue_webhook_rpc(submission.id)

    return success_response('submission accepted')


@public.route('/whoami')
def public_whoami():
    """
    Figure out who you are

    :return:
    """
    u: User = current_user()
    if u is None:
        return success_response(None)
    return success_response({
        'user': u.data,
        'classes': list(map(lambda c: c.data, u.classes))
    })
