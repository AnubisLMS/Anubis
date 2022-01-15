from datetime import datetime, timedelta
from typing import Union

from flask import Blueprint, request

from anubis.lms.assignments import get_assignment_due_date
from anubis.lms.submissions import get_submissions, init_submission, reject_late_submission
from anubis.lms.webhook import check_repo, guess_github_repo_owner, parse_webhook
from anubis.models import Assignment, AssignmentRepo, Course, InCourse, Submission, User, db
from anubis.utils.cache import cache
from anubis.utils.data import is_debug, req_assert
from anubis.utils.http import error_response, success_response
from anubis.utils.http.decorators import json_response
from anubis.utils.logging import logger
from anubis.utils.rpc import enqueue_autograde_pipeline

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
        message="Unable to verify webhook",
    )

    # Load the basics from the webhook
    repo_url, repo_name, pusher_username, commit, before, ref = parse_webhook(request.json)

    # Attempt to find records for the relevant models
    assignment = Assignment.query.filter(Assignment.unique_code.in_(repo_name.split("-"))).first()

    # Verify that we can match this push to an assignment
    req_assert(assignment is not None, message="assignment not found", status_code=406)

    # Get github username from the repository name
    user, netid = guess_github_repo_owner(assignment, repo_name)

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
                "pusher": pusher_username,
                "commit": commit,
            },
        )

        repo = check_repo(assignment, repo_url, user, netid)

        if repo.owner_id == None:
            return success_response("initial dangling")

        return success_response("initial commit")

    repo = (
        AssignmentRepo.query.join(Assignment)
        .join(Course)
        .join(InCourse)
        .join(User)
        .filter(
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

    org_name = assignment.course.github_org
    if not is_debug() and org_name is not None and org_name != "":
        # Make sure that the repo we're about to process actually belongs to
        # a github organization that matches the course.
        if not repo_url.startswith(f"https://github.com/{org_name}"):
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
        repo = check_repo(assignment, repo_url, user, netid)

    req_assert(
        ref == "refs/heads/master" or ref == "refs/heads/main",
        message="not a push to master or main",
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
        return success_response({"status": "already created"})

    # Create the related submission models
    init_submission(submission)

    # If a user has not given us their github username
    # the submission will stay in a "dangling" state
    req_assert(user is not None, message="dangling submission")

    # If the github username is not found, create a dangling submission
    if assignment.autograde_enabled:

        # Check that the current assignment is still accepting submissions
        if not assignment.accept_late and datetime.now() < get_assignment_due_date(user, assignment, grace=True):
            reject_late_submission(submission)

    else:
        submission.processed = True
        submission.accepted = False
        submission.state = "autograde disabled for this assignment"

    db.session.commit()

    # If the submission was accepted, then enqueue the job
    if submission.accepted and user is not None:
        enqueue_autograde_pipeline(submission.id)

    # Delete cached submissions
    cache.delete_memoized(get_submissions, user.netid)
    cache.delete_memoized(get_submissions, user.netid, assignment.course_id)
    cache.delete_memoized(get_submissions, user.netid, assignment.course_id, assignment.id)

    return success_response("submission accepted")
