from anubis.models import Submission, AssignmentRepo, User, db
from anubis.utils.http import error_response, success_response
from anubis.utils.rpc import enqueue_webhook


def bulk_regrade_submission(submissions):
    """
    Regrade a batch of submissions
    :param submissions:
    :return:
    """
    response = []
    for submission in submissions:
        response.append(regrade_submission(submission))
    return response


def regrade_submission(submission):
    """
    Regrade a submission

    :param submission: Union[Submissions, int]
    :return: dict response
    """

    if isinstance(submission, str):
        submission = Submission.query.filter_by(id=submission).first()
        if submission is None:
            return error_response("could not find submission")

    if not submission.processed:
        return error_response("submission currently being processed")

    submission.processed = False
    submission.state = "Waiting for resources..."
    submission.init_submission_models()

    enqueue_webhook(submission.id)

    return success_response({"message": "regrade started"})


def fix_dangling():
    """
    Try to connect repos that do not have an owner.

    :return:
    """
    fixed = []

    dangling_repos = AssignmentRepo.query.filter(AssignmentRepo.owner_id == None).all()
    for dr in dangling_repos:
        owner = User.query.filter(User.github_username == dr.github_username).first()

        if owner is not None:
            dr.owner_id = owner.id
            db.session.add_all((dr, owner))
            db.session.commit()

            for s in dr.submissions:
                s.owner_id = owner.id
                db.session.add(s)
                db.session.commit()
                fixed.append(s.data)
                enqueue_webhook(s.id)

    dangling_submissions = Submission.query.filter(Submission.owner_id == None).all()
    for s in dangling_submissions:
        dr = AssignmentRepo.query.filter(
            AssignmentRepo.id == s.assignment_repo_id
        ).first()

        owner = User.query.filter(User.github_username == dr.github_username).first()

        if owner is not None:
            dr.owner_id = owner.id
            db.session.add_all((dr, owner))
            db.session.commit()

            s.owner_id = owner.id
            db.session.add(s)
            db.session.commit()
            fixed.append(s.data)
            enqueue_webhook(s.id)

    return fixed
