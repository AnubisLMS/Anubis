from flask import Blueprint

from anubis.models import Assignment, User
from anubis.utils.assignments import assignment_sync
from anubis.utils.decorators import load_from_id, json_response, json_endpoint
from anubis.utils.elastic import log_endpoint
from anubis.utils.http import error_response, success_response
from anubis.utils.questions import get_assigned_questions
from anubis.utils.auth import require_admin

assignments = Blueprint("admin-assignments", __name__, url_prefix="/admin/assignments")


@assignments.route("/assignment/<int:id>/questions/get/<string:netid>")
@require_admin
@log_endpoint("cli", lambda: "question get")
@load_from_id(Assignment, verify_owner=False)
@json_response
def private_assignment_id_questions_get_netid(assignment: Assignment, netid: str):
    """
    Get questions assigned to a given student.

    :param assignment:
    :param netid:
    :return:
    """
    user = User.query.filter_by(netid=netid).first()
    if user is None:
        return error_response("user not found")

    return success_response(
        {
            "netid": user.netid,
            "questions": get_assigned_questions(assignment.id, user.id),
        }
    )


@assignments.route("/assignment/sync", methods=["POST"])
@require_admin
@log_endpoint("cli", lambda: "assignment-sync")
@json_endpoint(required_fields=[("assignment", dict)])
def private_assignment_sync(assignment_data: dict):
    """
    Sync assignment data from the CLI. This should be used to create and update assignment data.

    body = {
      "assignment": {
        "name": "{name}",
        "class": "CS-UY 3224",
        "hidden": true,
        "github_classroom_url": "",
        "unique_code": "{code}",
        "pipeline_image": "registry.osiris.services/anubis/assignment/{code}",
        "date": {
          "release": "{now}",
          "due": "{week_from_now}",
          "grace": "{week_from_now}"
        },
        "description": "This is a very long description that encompases the entire assignment\n",
        "questions": [
          {
            "sequence": 1,
            "questions": [
              {
                "q": "What is 3*4?",
                "a": "12"
              },
              {
                "q": "What is 3*2",
                "a": "6"
              }
            ]
          },
          {
            "sequence": 2,
            "questions": [
              {
                "q": "What is sqrt(144)?",
                "a": "12"
              }
            ]
          }
        ]
      }
    }

    response = {
      assignment : {}
      questions: {
        accepted: [ ... ]
        ignored: [ ... ]
        rejected: [ ... ]
      }
    }

    :param assignment_data:
    :param test_data:
    :param question_data:
    :return:
    """

    # Create or update assignment
    message, success = assignment_sync(assignment_data)

    # If there was an error, pass it back
    if not success:
        return error_response(message), 406

    # Return
    return success_response(message)
