import string
from datetime import datetime, timedelta
from typing import List, Dict

from flask import request, redirect, Blueprint, make_response

from anubis.models import Assignment, AssignmentRepo, AssignedStudentQuestion, TheiaSession
from anubis.models import Submission
from anubis.models import db, User, Class_, InClass
from anubis.utils.auth import current_user
from anubis.utils.auth import get_token
from anubis.utils.cache import cache
from anubis.utils.data import error_response, success_response, is_debug
from anubis.utils.data import fix_dangling
from anubis.utils.data import get_classes, get_assignments, get_submissions, get_assigned_questions
from anubis.utils.data import regrade_submission
from anubis.utils.data import theia_redirect, theia_list_all, theia_poll_ide, theia_redirect_url
from anubis.utils.decorators import json_endpoint, json_response, require_user, load_from_id
from anubis.utils.elastic import log_endpoint, esindex
from anubis.utils.http import get_request_ip
from anubis.utils.logger import logger
from anubis.utils.oauth import OAUTH_REMOTE_APP as provider
from anubis.utils.redis_queue import enqueue_ide_initialize, enqueue_webhook, enqueue_ide_stop

public = Blueprint('public', __name__, url_prefix='/public')


def webhook_log_msg():
    if request.headers.get('Content-Type', None) == 'application/json' and \
    request.headers.get('X-GitHub-Event', None) == 'push':
        return request.json['pusher']['name']
    return None


@public.route('/memes')
@log_endpoint('rick-roll', lambda: 'rick-roll')
def public_memes():
    logger.info('rick-roll')
    return redirect('https://www.youtube.com/watch?v=dQw4w9WgXcQ&autoplay=1')


@public.route('/login')
@log_endpoint('public-login', lambda: 'login')
def public_login():
    return provider.authorize(
        callback='https://anubis.osiris.services/api/public/oauth'
    )


@public.route('/logout')
@log_endpoint('public-logout', lambda: 'logout')
def public_logout():
    r = make_response(redirect('/'))
    r.set_cookie('token', '')
    return r


@public.route('/oauth')
@log_endpoint('public-oauth', lambda: 'oauth')
def public_oauth():
    next_url = request.args.get('next') or '/courses'
    resp = provider.authorized_response()
    if resp is None or 'access_token' not in resp:
        return 'Access Denied'

    user_data = provider.get('userinfo?schema=openid', token=(resp['access_token'],))

    netid = user_data.data['netid']
    name = user_data.data['firstname'] + ' ' + user_data.data['lastname']

    u = User.query.filter(User.netid == netid).first()
    if u is None:
        u = User(netid=netid, name=name, is_admin=False)
        db.session.add(u)
        db.session.commit()

    if u.github_username is None:
        next_url = '/set-github-username'

    fix_dangling()

    r = make_response(redirect(next_url))
    r.set_cookie('token', get_token(u.netid))

    return r


@public.route('/set-github-username')
@require_user
@log_endpoint('public-set-github-username', lambda: 'github username set')
@json_response
def public_set_github_username():
    u: User = current_user()

    github_username = request.args.get('github_username', default=None)
    if github_username is None:
        return error_response('missing field')
    github_username = github_username.strip()

    if any(i in string.whitespace for i in github_username):
        return error_response('Your username can not have spaces')

    if not (all(i in (string.ascii_letters + string.digits + '-') for i in github_username)
            and not github_username.startswith('-') and not github_username.endswith('-')):
        return error_response('Github usernames may only contain alphanumeric characters '
                              'or single hyphens, and cannot begin or end with a hyphen.')

    logger.info(str(u.last_updated))
    logger.info(str(u.last_updated + timedelta(hours=1)) + ' - ' + str(datetime.now()))

    if u.github_username is not None and u.last_updated + timedelta(hours=1) < datetime.now():
        return error_response('Github usernames can only be '
                              'changed one hour after first setting. '
                              'Email the TAs to reset your github username.')  # reject their github username change

    u.github_username = github_username
    db.session.add(u)
    db.session.commit()

    return success_response(github_username)


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


@public.route('/assignment/questions/get/<int:id>')
@require_user
@log_endpoint('public-questions-get', lambda: 'get questions')
@load_from_id(Assignment, verify_owner=False)
@json_response
def public_assignment_questions_id(assignment: Assignment):
    """
    Get assigned questions for the current user for a given assignment.

    :param assignment:
    :return:
    """
    # Load current user
    user: User = current_user()

    return success_response({
        'questions': get_assigned_questions(assignment.id, user.id)
    })


@public.route('/assignment/questions/save/<int:id>')
@require_user
@log_endpoint('public-questions-save', lambda: 'save questions')
@load_from_id(AssignedStudentQuestion, verify_owner=True)
@json_endpoint(required_fields=[('response', str)])
def public_assignment_questions_save_id(assigned_question: AssignedStudentQuestion, response: str, **kwargs):
    """
    Save response for a given assignment question

    :param assigned_question:
    :param response:
    :param kwargs:
    :return:
    """
    assigned_question.response = response

    db.session.add(assigned_question)
    db.session.commit()

    return success_response('Success')


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
    assignment_id = request.args.get('assignment_id', default=None)

    # Load current user
    user: User = current_user()

    # Get submissions through cached function
    return success_response({
        'submissions': get_submissions(
            user.netid,
            class_name=class_name,
            assignment_name=assignment_name,
            assignment_id=assignment_id
        )
    })


@public.route('/submission/<string:commit>')
@require_user
@log_endpoint('public-submission-commit', lambda: 'get submission {}'.format(request.path))
@json_response
@cache.memoize(timeout=1, unless=is_debug)
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
    return success_response({'submission': s.full_data})


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
    user: User = current_user()

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
    repo_url = webhook['repository']['url']
    github_username = webhook['pusher']['name']
    commit = webhook['after']
    assignment_name = webhook['repository']['name'][:-(len(github_username) + 1)]

    # Attempt to find records for the relevant models
    assignment = Assignment.query.filter(
        Assignment.unique_code.in_(webhook['repository']['name'].split('-'))
    ).first()
    user = User.query.filter(User.github_username == github_username).first()

    # The before Hash will be all 0s on for the first hash.
    # We will want to ignore both this first push (the initialization of the repo)
    # and all branches that are not master.
    if webhook['before'] == '0000000000000000000000000000000000000000':
        # Record that a new repo was created (and therefore, someone just started their assignment)
        logger.info('new student repo ', extra={
            'repo_url': repo_url, 'github_username': github_username,
            'assignment_name': assignment_name, 'commit': commit,
        })

        repo_name_split = webhook['repository']['name'].split('-')
        unique_code_index = repo_name_split.index(assignment.unique_code)
        repo_name_split = repo_name_split[unique_code_index+1:]
        github_username1 = '-'.join(repo_name_split)
        github_username2 = '-'.join(repo_name_split[:-1])
        user = User.query.filter(
            User.github_username.in_([github_username1, github_username2])
        ).first()

        if user is not None:
            repo = AssignmentRepo(owner=user, assignment=assignment,
                                  repo_url=repo_url, github_username=user.github_username)
            db.session.add(repo)
            db.session.commit()

        esindex('new-repo', repo_url=repo_url, assignment=str(assignment))
        return success_response('initial commit')

    # Verify that we can match this push to an assignment
    if assignment is None:
        logger.error('Could not find assignment', extra={
            'repo_url': repo_url, 'github_username': github_username,
            'assignment_name': assignment_name, 'commit': commit,
        })
        return error_response('assignment not found'), 406

    repo = AssignmentRepo.query.join(Assignment).join(Class_).join(InClass).join(User).filter(
        User.github_username == github_username,
        Assignment.unique_code == assignment.unique_code,
        AssignmentRepo.repo_url == repo_url,
    ).first()

    logger.debug('webhook data', extra={
        'github_username': github_username, 'assignment': assignment.name,
        'repo_url': repo_url, 'commit': commit, 'unique_code': assignment.unique_code
    })

    if not is_debug():
        # Make sure that the repo we're about to process actually belongs to our organization
        if not webhook['repository']['full_name'].startswith('os3224/'):
            logger.error('Invalid github organization in webhook.', extra={
                'repo_url': repo_url, 'github_username': github_username,
                'assignment_name': assignment_name, 'commit': commit,
            })
            return error_response('invalid repo'), 406

    # if we dont have a record of the repo, then add it
    if repo is None:
        repo = AssignmentRepo(owner=user, assignment=assignment, repo_url=repo_url, github_username=github_username)
        db.session.add(repo)
        db.session.commit()

    if webhook['ref'] != 'refs/heads/master':
        logger.warning('not push to master', extra={
            'repo_url': repo_url, 'github_username': github_username,
            'assignment_name': assignment_name, 'commit': commit,
        })
        return error_response('not push to master')

    # Create a shiny new submission
    submission = Submission(assignment=assignment, repo=repo, owner=user, commit=commit,
                            state='Waiting for resources...')
    db.session.add(submission)
    db.session.commit()

    # Create the related submission models
    submission.init_submission_models()

    # If a user has not given us their github username
    # the submission will stay in a "dangling" state
    if user is None:
        logger.warning('dangling submission from {}'.format(github_username), extra={
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
    enqueue_webhook(submission.id)

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


@public.route('/ide/list')
@log_endpoint('ide-list', lambda: 'ide-list')
@require_user
@json_response
def public_ide_list():
    """
    List all sessions, active and inactive

    :return:
    """
    user: User = current_user()

    return success_response({
        'sessions': theia_list_all(user.id)
    })


@public.route('/ide/stop/<int:theia_session_id>')
@log_endpoint('stop-theia-session', lambda: 'stop-theia-session')
@require_user
def public_ide_stop(theia_session_id: int) -> Dict[str, str]:
    user: User = current_user()

    theia_session: TheiaSession = TheiaSession.query.filter(
        TheiaSession.id == theia_session_id,
        TheiaSession.owner_id == user.id,
    ).first()
    if theia_session is None:
        return redirect('/ide?error=Can not find session.')

    theia_session.active = False
    theia_session.ended = datetime.now()
    theia_session.state = 'Ending'
    db.session.commit()

    enqueue_ide_stop(theia_session.id)

    return redirect('/ide')


@public.route('/ide/poll/<int:theia_session_id>')
@log_endpoint('ide-poll-id', lambda: 'ide-poll')
@require_user
@json_response
def public_ide_poll(theia_session_id: int) -> Dict[str, str]:
    """
    Slightly cached endpoint for polling for session data.

    :param theia_session_id:
    :return:
    """
    user: User = current_user()

    session_data = theia_poll_ide(theia_session_id, user.id)
    if session_data is None:
        return error_response('Can not find session')

    return success_response({
        'session': session_data
    })


@public.route('/ide/redirect-url/<int:theia_session_id>')
@log_endpoint('ide-redirect-url', lambda: 'ide-redirect-url')
@require_user
@json_response
def public_ide_redirect_url(theia_session_id: int) -> Dict[str, str]:
    """
    Get the redirect url for a given session

    :param theia_session_id:
    :return:
    """
    user: User = current_user()

    theia_session: TheiaSession = TheiaSession.query.filter(
        TheiaSession.id == theia_session_id,
        TheiaSession.owner_id == user.id,
    ).first()
    if theia_session is None:
        return error_response('Can not find session')

    return success_response({
        'redirect': theia_redirect_url(theia_session, user)
    })


@public.route('/ide/initialize/<int:id>')
@log_endpoint('ide-initialize', lambda: 'ide-initialize')
@require_user
@load_from_id(Assignment, verify_owner=False)
def public_ide_initialize(assignment: Assignment):
    """
    Redirect to theia proxy.

    :param assignment:
    :return:
    """
    user: User = current_user()

    if not assignment.ide_enabled:
        return error_response('Theia not enabled for this assignment.')

    # Check for existing active session
    active_session = TheiaSession.query.join(Assignment).filter(
        TheiaSession.owner_id == user.id,
        TheiaSession.assignment_id == assignment.id,
        TheiaSession.active == True,
        Assignment.release_date <= datetime.now(),
        Assignment.due_date + timedelta(days=7) >= datetime.now(),
    ).first()
    if active_session is not None:
        return theia_redirect(active_session, user)

    if datetime.now() <= assignment.release_date:
        return redirect('/ide?error=Assignment has not been released.')

    if assignment.due_date + timedelta(days=3*7) <= datetime.now():
        return redirect('/ide?error=Assignment due date passed over 3 weeks ago.')

    # Make sure we have a repo we can use
    repo = AssignmentRepo.query.filter(
        AssignmentRepo.owner_id == user.id,
        AssignmentRepo.assignment_id == assignment.id,
    ).first()
    if repo is None:
        return redirect('/courses/assignments?error=Please create your assignment repo first.')

    # Create a new session
    session = TheiaSession(
        owner_id=user.id,
        assignment_id=assignment.id,
        repo_id=repo.id,
        active=True,
        state='Initializing',
    )
    db.session.add(session)
    db.session.commit()

    # Send kube resource initialization rpc job
    enqueue_ide_initialize(session.id)

    # Redirect to proxy
    return redirect('/ide')
