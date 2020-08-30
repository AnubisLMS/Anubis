import logging
import traceback

from flask import request, redirect, Blueprint
from sqlalchemy.exc import IntegrityError

from anubis.models import Assignment, AssignmentRepo
from anubis.models import Submission
from anubis.models import db, User, Class_, InClass
from anubis.utils.auth import current_user
from anubis.utils.data import error_response, success_response, is_debug
from anubis.utils.data import get_classes, get_assignments, get_submissions
from anubis.utils.data import regrade_submission, enqueue_webhook_rpc
from anubis.utils.decorators import json_response, require_user
from anubis.utils.elastic import log_endpoint, esindex
from anubis.utils.http import get_request_ip

public = Blueprint('public', __name__, url_prefix='/public')


@public.route('/classes')
@require_user
@log_endpoint('public-classes', lambda: 'get classes {}'.format(get_request_ip()))
@json_response
def public_classes():
    """
    Get class data for current user

    :return:
    """
    user: User = current_user()
    return success_response({
        'classes': get_classes(user.netid)
    })


@public.route('/assignments')
@require_user
@log_endpoint('public-assignments', lambda: 'get assignments {}'.format(get_request_ip()))
@json_response
def public_assignments():
    """
    Get all the assignments for a user. Optionally specify a class
    name as a get query.

    /api/public/assignments?class=Intro to OS

    :return: { "assignments": [ assignment.data ] }
    """

    # Get optional class filter from get query
    class_name = request.args.get('class', default=None)

    # Load current user
    user: User = current_user()

    # Get (possibly cached) assignment data
    assignment_data = get_assignments(user.netid, class_name)

    # Iterate over assignments, getting their data
    return success_response({
        'assignments': assignment_data
    })


@public.route('/submissions')
@require_user
@log_endpoint('public-submissions', lambda: 'get submissions {}'.format(get_request_ip()))
@json_response
def public_submissions():
    """
    Get all submissions for a given student. Optionally specify class,
    and assignment name filters in get query.


    /api/public/submissions
    /api/public/submissions?class=Intro to OS
    /api/public/submissions?assignment=Assignment 1: uniq
    /api/public/submissions?class=Intro to OS&assignment=Assignment 1: uniq

    :return:
    """
    # Get optional filters
    class_name = request.args.get('class', default=None)
    assignment_name = request.args.get('assignment', default=None)

    # Load current user
    user: User = current_user()

    # Get submissions through cached function
    return success_response({
        'submissions': get_submissions(
            user.netid,
            class_name=class_name,
            assignment_name=assignment_name)
    })


@public.route('/submission/<string:commit>')
@require_user
@log_endpoint('public-submission-commit', lambda: 'get submission {}'.format(request.path))
@json_response
def public_submission(commit: str):
    """
    Get submission data for a given commit.

    :param commit:
    :return:
    """
    # Get current user
    user: User = current_user()

    # Try to find commit (verifying ownership)
    s = Submission.query.join(User).filter(
        User.netid == user.netid,
        Submission.commit == commit
    ).first()

    # Make sure we caught one
    if s is None:
        return error_response('Commit does not exist'), 406

    # Hand back submission
    return success_response({'submission': s.data})


def webhook_log_msg():
    if request.headers.get('Content-Type', None) == 'application/json' and \
    request.headers.get('X-GitHub-Event', None) == 'push':
        return request.json['pusher']['name']
    return None


@public.route('/memes')
@log_endpoint('rick-roll', lambda: 'rick-roll')
def public_memes():
    logging.info('rick-roll')
    return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ')


@public.route('/regrade/<commit>')
@require_user
@log_endpoint('regrade-request', lambda: 'submission regrade request ' + request.path)
@json_response
def public_regrade_commit(commit=None):
    """
    This route will get hit whenever someone clicks the regrade button on a
    processed assignment. It should do some validity checks on the commit and
    netid, then reset the submission and re-enqueue the submission job.
    """
    if commit is None:
        return error_response('incomplete_request'), 406

    # Load current user
    user: User = User.current_user()

    # Find the submission
    submission: Submission = Submission.query.join(User).filter(
        Submission.commit == commit,
        User.netid == user.netid
    ).first()

    # Verify Ownership
    if submission is None:
        return error_response('invalid commit hash or netid'), 406

    # Regrade
    return regrade_submission(submission)


# dont think we need GET here
@public.route('/webhook', methods=['POST'])
@log_endpoint('webhook', webhook_log_msg)
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
    unique_code = assignment_name.split('-')[-1]

    # Attempt to find records for the relevant models
    assignment = Assignment.query.filter_by(unique_code=unique_code).first()
    user = User.query.filter(User.github_username == github_username).first()
    repo = AssignmentRepo.query.Join(Assignment).Join(Class_).join(InClass).join(User).filter(
        User.github_username == github_username,
        Assignment.name == assignment_name,
    ).first()

    # Verify that we can match this push to an assignment
    if assignment is None:
        logging.error('Could not find assignment', extra={
            'repo_url': repo_url, 'github_username': github_username,
            'assignment_name': assignment_name, 'commit': commit,
        })
        return error_response('assignment not found'), 406

    if not is_debug():
        # Make sure that the repo we're about to process actually belongs to our organization
        if not webhook['repository']['full_name'].startswith('os3224/'):
            logging.error('Invalid github organization in webhook.', extra={
                'repo_url': repo_url, 'github_username': github_username,
                'assignment_name': assignment_name, 'commit': commit,
            })
            return error_response('invalid repo'), 406

    # if we dont have a record of the repo, then add it
    if repo is None:
        repo = AssignmentRepo(owner=user, assignment=assignment, repo_url=repo_url)
        db.session.add(repo)
        db.session.commit()

    # The before Hash will be all 0s on for the first hash.
    # We will want to ignore both this first push (the initialization of the repo)
    # and all branches that are not master.
    if webhook['before'] == '0000000000000000000000000000000000000000':
        # Record that a new repo was created (and therefore, someone just started their assignment)
        logging.info('new student repo ', extra={
            'repo_url': repo_url, 'github_username': github_username,
            'assignment_name': assignment_name, 'commit': commit,
        })
        esindex('new-repo', github_username=github_username, repo_url=repo_url, assignment=str(assignment))
        return success_response('initial commit')

    if webhook['ref'] != 'refs/heads/master':
        logging.warn('not push to master', extra={
            'repo_url': repo_url, 'github_username': github_username,
            'assignment_name': assignment_name, 'commit': commit,
        })
        return error_response('not push to master')

    # Create a shiny new submission
    submission = Submission(assignment=assignment, owner=user, commit=commit, state='Enqueued')
    db.session.add(submission)
    db.session.commit()

    # Create the related submission models
    submission.init_submission_models()

    # If a user has not given us their github username
    # the submission will stay in a "dangling" state
    if user is None:
        logging.warn('dangling submission from {}'.format(github_username), extra={
            'repo_url': repo_url, 'github_username': github_username,
            'assignment_name': assignment_name, 'commit': commit,
        })
        esindex(
            type='error',
            logs='dangling submission by: ' + github_username,
            submission=submission.data,
            neitd=None,
        )
        return error_response('dangling submission')

    # Log the submission
    esindex(
        index='submission',
        processed=0,
        error=-1,
        passed=-1,
        netid=submission.netid,
        commit=submission.commit,
    )

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
        'classes': get_classes(u.netid),
        'assignments': get_assignments(u.netid),
    })
