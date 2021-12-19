from anubis.models import (
    AssignedQuestionResponse,
    AssignedStudentQuestion,
    Assignment,
    AssignmentQuestion,
    AssignmentRepo,
    AssignmentTest,
    Course,
    InCourse,
    LateException,
    LectureNotes,
    ProfessorForCourse,
    StaticFile,
    Submission,
    SubmissionBuild,
    SubmissionTestResult,
    TAForCourse,
    TheiaSession,
    TheiaImage,
    TheiaImageTag,
    User,
    db,
)


def clear_database():
    # Yeet
    LateException.query.delete()
    TheiaSession.query.delete()
    AssignedQuestionResponse.query.delete()
    AssignedStudentQuestion.query.delete()
    AssignmentQuestion.query.delete()
    SubmissionTestResult.query.delete()
    SubmissionBuild.query.delete()
    Submission.query.delete()
    AssignmentRepo.query.delete()
    AssignmentTest.query.delete()
    InCourse.query.delete()
    Assignment.query.delete()
    TAForCourse.query.delete()
    ProfessorForCourse.query.delete()
    LectureNotes.query.delete()
    StaticFile.query.delete()
    Course.query.delete()
    TheiaImageTag.query.delete()
    TheiaImage.query.delete()
    User.query.delete()
    db.session.commit()