from datetime import datetime

from flask import Blueprint

from anubis.lms.courses import is_course_admin
from anubis.lms.repos import get_repos
from anubis.models import Assignment, AssignmentRepo
from anubis.utils.auth.http import require_user
from anubis.utils.auth.user import current_user
from anubis.utils.cache import cache
from anubis.utils.github.repos import create_assignment_student_repo, delete_assignment_repo
from anubis.utils.http import error_response, req_assert, success_response
from anubis.utils.http.decorators import json_response

repos_ = Blueprint("public-repos", __name__, url_prefix="/public/repos")


@repos_.get("")
@repos_.get("/list")
@require_user()
@json_response
def public_repos_list():
    """
    Get all unique repos for a user

    :return:
    """

    # Get all repos for the user
    repos = get_repos(current_user.id)

    # Pass them back
    return success_response({"repos": repos})


@repos_.get("/get/<string:assignment_id>")
@require_user()
@json_response
def public_repos_get(assignment_id: str):
    """
    Get all unique repos for a user

    :return:
    """

    assignment: Assignment = Assignment.query.filter(
        Assignment.id == assignment_id,
    ).first()

    # Verify assignment exists
    req_assert(assignment is not None, message="Assignment does not exist")

    # If it has not been released, make sure the current user is an admin
    if assignment.release_date > datetime.now():
        req_assert(
            is_course_admin(assignment.course_id, current_user.id),
            message="Assignment does not exist",
        )

    repo = AssignmentRepo.query.filter(
        AssignmentRepo.owner_id == current_user.id,
        AssignmentRepo.assignment_id == assignment.id,
    ).first()

    if repo is None:
        return success_response({"repo": None})

    # Pass them back
    return success_response({"repo": repo.data})


@repos_.post("/create/<string:assignment_id>")
@require_user()
@json_response
def public_repos_create(assignment_id: str):
    """
    Get all unique repos for a user

    :return:
    """

    if current_user.github_username == "" or current_user.github_username is None:
        return error_response("Please set github username on profile page")

    assignment: Assignment = Assignment.query.filter(
        Assignment.id == assignment_id,
    ).first()

    # Verify assignment exists
    req_assert(assignment is not None, message="Assignment does not exist")

    # If it has not been released, make sure the current user is an admin
    if assignment.release_date > datetime.now():
        req_assert(
            is_course_admin(assignment.course_id, current_user.id),
            message="Assignment does not exist",
        )

    repo = create_assignment_student_repo(current_user, assignment)

    req_assert(repo.repo_created, message="Repo could not be created")
    req_assert(
        repo.collaborator_configured,
        message="Student could not be added as a collaborator to repo",
    )

    # Pass them back
    return success_response({"repo": repo.data})


@repos_.delete("/delete/<string:assignment_id>")
@require_user()
@json_response
def public_repos_delete(assignment_id: str):
    """
    Get all unique repos for a user

    :return:
    """

    if current_user.github_username == "" or current_user.github_username is None:
        return error_response("Please set github username on profile page")

    assignment: Assignment = Assignment.query.filter(
        Assignment.id == assignment_id,
    ).first()

    # Verify assignment exists
    req_assert(assignment is not None, message="Assignment does not exist")

    # If it has not been released, make sure the current user is an admin
    if assignment.release_date > datetime.now():
        req_assert(
            is_course_admin(assignment.course_id, current_user.id),
            message="Assignment does not exist",
        )

    # Get the repo from db
    repo: AssignmentRepo = AssignmentRepo.query.filter(
        AssignmentRepo.assignment_id == assignment.id,
        AssignmentRepo.owner_id == current_user.id,
    ).first()

    # Make sure the repo exists
    req_assert(repo is not None, message="Repo does not exist")

    # If the repo is shared, then student can not delete
    req_assert(not repo.shared, message="Repo is shared. Please reach out to Anubis support to delete/reset this repo.")

    # Delete the repo
    delete_assignment_repo(current_user, assignment)

    # Delete cache entry
    cache.delete_memoized(get_repos, current_user.id)

    # Pass them back
    return success_response({"status": "Github Repo & Submissions deleted"})
