from datetime import datetime

from ..app import db
from .user import User
from .assignment import AssignmentTest, Assignment


class Submission(db.Model):
    """
    Submissions
    """
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(User.id), index=True, nullable=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey(Assignment.id), index=True, nullable=False)
    github_username = db.Column(db.String(128), nullable=False)
    repo = db.Column(db.String(128), nullable=False)
    commit = db.Column(db.String(128), unique=True, index=True, nullable=False)
    processed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(True), default=datetime.now)

    student = db.relationship(User, backref='submissions')
    assignment = db.relationship(Assignment)

    @property
    def url(self):
        return 'https://anubis.osiris.services/view/{}/{}'.format(self.commit, self.netid)

    @property
    def netid(self):
        if self.student is not None:
            return self.student.netid
        return 'null'

    @property
    def data(self):
        return {
            'id': self.id,
            'netid': self.netid,
            'assignment': self.assignment.name,
            'url': self.url,
            'commit': self.commit,
            'processed': self.processed,
            'timestamp': str(self.timestamp),

            # Connected models
            'test_results': [r.data for r in self.test_results],
            'submission_build': self.build.data,
        }


class SubmissionTestResult(db.Model):
    __tablename__ = 'submission_test_result'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey(Submission.id), primary_key=True)
    assignment_test_id = db.Column(db.Integer, db.ForeignKey(Submission.id), primary_key=True)
    stdout = db.Column(db.Text)
    errors = db.Column(db.Text)
    passed = db.Column(db.Boolean)

    submission = db.relationship(Submission, backref='test_results')
    assignment_test = db.relationship(AssignmentTest, backref='test_results')

    @property
    def data(self):
        return {
            'testname': self.testname,
            'errors': self.errors,
            'passed': self.passed,
            'stdout': self.stdout
        }

    def __str__(self):
        return 'testname: {}\nerrors: {}\npassed: {}\n'.format(
            self.testname,
            self.errors,
            self.passed,
        )


class SubmissionBuild(db.Model):
    __tablename__ = 'submission_build'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey(Submission.id), index=True)

    stdout = db.Column(db.Text)

    submission = db.relationship('Submissions', backref='build', uselist=False)

    @property
    def data(self):
        return {
            'stdout': self.stdout,
        }