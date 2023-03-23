from flask import Blueprint

from anubis.lms.courses import assert_course_context
from anubis.models import SubmissionTestResult, Submission, SubmissionBuild, TheiaSession, db
from anubis.utils.auth.http import require_admin
from anubis.utils.data import req_assert
from anubis.utils.http import success_response
from anubis.utils.http.decorators import json_response, load_from_id

submissions_ = Blueprint("admin-submissions", __name__, url_prefix="/admin/submissions")


@submissions_.delete('/delete/<string:id>')
@require_admin()
@load_from_id(Submission)
@json_response
def admin_submissions_delete_id(submission: Submission):
    """
    Delete a student submission as an admin.

    :param submission:
    :return:
    """

    # Verify that current user is allowed to manage submission
    assert_course_context(submission)

    # Check if submission is tied to an IDE session
    theia_session: TheiaSession | None = TheiaSession.query.filter(TheiaSession.submission_id == submission.id).first()
    if theia_session is not None:

        # Make sure that the IDE session is not currently active (ie: open)
        req_assert(
            not theia_session.active,
            message=f"Cannot delete a submission that is tied to a currently active IDE. "
                    f"Stop IDE then delete submission."
        )

        # Unlink submission from theia session
        theia_session.submission_id = None

    # Delete submission sub-table rows
    SubmissionBuild.query.filter(SubmissionBuild.submission_id == submission.id).delete()
    SubmissionTestResult.query.filter(SubmissionTestResult.submission_id == submission.id).delete()

    # Delete submission
    Submission.query.filter(Submission.id == submission.id).delete()

    # Commit deletes
    db.session.commit()

    return success_response({
        'status':  'Submission deleted',
        'variant': 'warning',
    })
