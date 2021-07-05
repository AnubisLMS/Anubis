from datetime import datetime, timedelta
from typing import Union

from flask import Blueprint, request

from anubis.models import (
    Assignment,
    User,
    AssignmentRepo,
    db,
    Course,
    InCourse,
    Submission,
)
from anubis.utils.data import is_debug, req_assert
from anubis.utils.http.decorators import json_response
from anubis.utils.http.https import error_response, success_response
from anubis.utils.lms.assignments import get_assignment_due_date
from anubis.utils.lms.submissions import get_submissions
from anubis.utils.lms.submissions import reject_late_submission, init_submission
from anubis.utils.lms.webhook import parse_webhook, guess_github_username, check_repo
from anubis.utils.services.cache import cache
from anubis.utils.services.logger import logger
from anubis.utils.services.rpc import enqueue_autograde_pipeline

webhook = Blueprint("public-webhook", __name__, url_prefix="/public/webhook")


def webhook_log_msg() -> Union[str, None]:
    """
    Log message for the webhook. We log the

    :return:
    """

    # Get the content type from the headers
    content_type = request.headers.get("Content-Type", None)

    # Get the github event header
    x_github_event = request.headers.get("X-GitHub-Event", None)

    # If the content type is json, and the github event was a push,
    # then log the repository name
    if content_type == "application/json" and x_github_event == "push":
        return request.json.get("repository", {}).get("name", None)

    return None


@webhook.route("/", methods=["POST"])
@webhook.route("/backup", methods=["POST"])
@json_response
def public_webhook():
    """
    This route should be hit by the github when a push happens.
    We should take the the github repo url and enqueue it as a job.

    :return:
    """

    content_type = request.headers.get("Content-Type", None)
    x_github_event = request.headers.get("X-GitHub-Event", None)

    # Verify some expected headers
    req_assert(
        content_type == "application/json" and x_github_event == "push",
        message='Unable to verify webhook'
    )

    # Load the basics from the webhook
    repo_url, repo_name, pusher_username, commit, before, ref = parse_webhook(request.json)

    # Attempt to find records for the relevant models
    assignment = Assignment.query.filter(
        Assignment.unique_code.in_(repo_name.split("-"))
    ).first()

    # Verify that we can match this push to an assignment
    req_assert(assignment is not None, message='assignment not found', status_code=406)

    # Get github username from the repository name
    user, github_username_guess = guess_github_username(assignment, repo_name)

    # The before Hash will be all 0s on for the first hash.
    # We will want to ignore both this first push (the initialization of the repo)
    # and all branches that are not master.
    if before == "0000000000000000000000000000000000000000":
        # Record that a new repo was created (and therefore, someone just
        # started their assignment)
        logger.debug(
            "new student repo ",
            extra={
                "repo_url": repo_url,
                "github_username": github_username_guess,
                "pusher": pusher_username,
                "commit": commit,
            },
        )

        repo = check_repo(assignment, repo_url, github_username_guess, user)

        if repo.owner_id == None:
            return success_response("initial dangling")
            
        return success_response("initial commit")

    repo = (
        AssignmentRepo.query
            .join(Assignment).join(Course).join(InCourse).join(User)
            .filter(
            User.github_username == github_username_guess,
            Assignment.unique_code == assignment.unique_code,
            AssignmentRepo.repo_url == repo_url,
        )
            .first()
    )

    logger.debug(
        "webhook data",
        extra={
            "assignment": assignment.name,
            "repo_url": repo_url,
            "commit": commit,
            "unique_code": assignment.unique_code,
        },
    )

    if not is_debug():
        # Make sure that the repo we're about to process actually belongs to
        # a github organization that matches a course.
        if not repo_url.startswith(assignment.course.github_org_url):
            logger.error(
                "Invalid github organization in webhook.",
                extra={
                    "repo_url": repo_url,
                    "pusher_username": pusher_username,
                    "commit": commit,
                },
            )
            return error_response("invalid repo"), 406

    # if we dont have a record of the repo, then add it
    if repo is None:
        repo = check_repo(assignment, repo_url, github_username_guess, user)

    req_assert(
        ref == 'refs/heads/master' or ref == 'refs/heads/main',
        message='not a push to master or main',
    )

    # Try to find a submission matching the commit
    submission = Submission.query.filter_by(commit=commit).first()

    # If the submission does not exist, then create one
    if submission is None:
        # Create a shiny new submission
        submission = Submission(
            assignment=assignment,
            repo=repo,
            owner=user,
            commit=commit,
            state="Waiting for resources...",
        )
        db.session.add(submission)
        db.session.commit()

    # If the submission did already exist, then we can just pass
    # back that status
    elif submission.created < datetime.now() - timedelta(minutes=3):
        return success_response({'status': 'already created'})

    # Create the related submission models
    init_submission(submission)

    # If a user has not given us their github username
    # the submission will stay in a "dangling" state
    req_assert(user is not None, message='dangling submission')

    # If the github username is not found, create a dangling submission
    if assignment.autograde_enabled:

        # Check that the current assignment is still accepting submissions
        if not assignment.accept_late and datetime.now() < get_assignment_due_date(user, assignment):
            reject_late_submission(submission)

    else:
        submission.processed = True
        submission.accepted = False
        submission.state = 'autograde disabled for this assignment'

    db.session.commit()

    # If the submission was accepted, then enqueue the job
    if submission.accepted and user is not None:
        enqueue_autograde_pipeline(submission.id)

    # Delete cached submissions
    cache.delete_memoized(get_submissions, user.netid)
    cache.delete_memoized(get_submissions, user.netid, assignment.course_id)
    cache.delete_memoized(get_submissions, user.netid, assignment.course_id, assignment.id)

    return success_response("submission accepted")
