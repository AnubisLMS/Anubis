from flask import Blueprint

from flask import Blueprint

from anubis.github.repos import delete_assignment_repo
from anubis.lms.assignments import get_assignment_data
from anubis.lms.courses import assert_course_context
from anubis.lms.repos import get_repos
from anubis.models import Assignment, AssignmentRepo, User
from anubis.utils.auth.http import require_user
from anubis.utils.cache import cache
from anubis.utils.http import req_assert, success_response
from anubis.utils.http.decorators import json_response

repos_ = Blueprint("admin-repos", __name__, url_prefix="/admin/repos")


@repos_.delete("/delete/<string:repo_id>")
@require_user()
@json_response
def admin_repos_delete(repo_id: str):
    """
    Get all unique repos for a user

    :return:
    """

    # Get the repo from db
    repo: AssignmentRepo = AssignmentRepo.query.filter(
        AssignmentRepo.id == repo_id,
    ).first()

    # Make sure the repo exists
    req_assert(repo is not None, message="Repo does not exist")

    # Verify this admin is allowed to touch this repo
    assert_course_context(repo)

    # Get student and assignment
    student: User = User.query.filter(User.id == repo.owner_id).first()
    assignment: Assignment = Assignment.query.filter(Assignment.id == repo.assignment_id).first()

    # Verify they exist
    req_assert(student is not None, message="User does not exist")
    req_assert(assignment is not None, message="Assignment does not exist")

    # Verify that the current course context, and the assignment course match
    assert_course_context(assignment)
    assert_course_context(student)


    # If the repo is shared, then student can not delete
    req_assert(not repo.shared, message="Repo is shared. Please reach out to Anubis support to delete/reset this repo.")

    # Delete the repo
    delete_assignment_repo(student, assignment)

    # Delete cache entry
    cache.delete_memoized(get_repos, student.id)

    # Clear cache entry
    cache.delete_memoized(get_assignment_data, student.id, repo.assignment_id)

    # Pass them back
    return success_response({"status": "Github Repo & Submissions deleted"})
