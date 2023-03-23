from anubis.ide.initialize import initialize_ide
from anubis.lms.shell_autograde import close_shell_autograde_ide_submission
from anubis.lms.shell_autograde import resume_submission
from anubis.models import db, TheiaImage, Assignment, AssignmentTest, User, SubmissionTestResult
from utils import Session, with_context

assignment_name = 'CS-UY 3224 Assignment 4'


def create_session(user: User):
    theia_image = TheiaImage.query.first()

    assignment = Assignment.query.filter_by(name=assignment_name).first()
    theia_session = initialize_ide(
        theia_image.id,
        assignment_id=assignment.id,
        autograde=True,
        owner_id=user.id,
    )
    return theia_session


@with_context
def test_resume_from_zero():
    session = Session("student", new=True)
    user = User.query.filter_by(netid=session.netid).first()

    theia_session = create_session(user)
    submission = theia_session.submission
    resume = resume_submission(submission)

    assert resume == ''


@with_context
def test_resume_from_one():
    session = Session("student", new=True)
    user = User.query.filter_by(netid=session.netid).first()

    theia_session = create_session(user)
    submission = theia_session.submission
    resume = resume_submission(submission)
    assert resume == ''
    test_results_one: SubmissionTestResult = SubmissionTestResult.query.join(AssignmentTest).filter(
        SubmissionTestResult.submission_id == submission.id
    ).order_by(AssignmentTest.order).first()
    assert test_results_one.assignment_test.name == 'helloworld'
    test_results_one.passed = True
    db.session.add(test_results_one)
    db.session.commit()
    close_shell_autograde_ide_submission(theia_session)

    theia_session = create_session(user)
    submission = theia_session.submission
    resume = resume_submission(submission)
    assert resume == 'helloworld'
    close_shell_autograde_ide_submission(theia_session)
