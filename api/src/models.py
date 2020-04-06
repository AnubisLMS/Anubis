from .app import db
from datetime import datetime
import json

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    netid = db.Column(db.String(128), index=True)
    github_username = db.Column(db.String(128), index=True)
    name = db.Column(db.String(128))

    @property
    def json(self):
        return {
            'id': self.id,
            'netid': self.netid,
            'github_username': self.github_username,
            'name': self.name,
        }


class Submissions(db.Model):
    """
    Submissions
    """
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    studentid = db.Column(db.Integer, db.ForeignKey('student.id'), index=True, nullable=True)
    assignmentid = db.Column(db.Integer, db.ForeignKey('assignments.id'), index=True, nullable=False)
    github_username = db.Column(db.String(128), nullable=False)
    repo = db.Column(db.String(128), nullable=False)
    commit = db.Column(db.String(128), unique=True, index=True, nullable=False)
    processed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(True), default=datetime.now)

    student = db.relationship('Student', backref='submissions')
    assignment = db.relationship('Assignment', backref='submissions')

    @property
    def url(self):
        return 'https://nyu.cool/view/{}/{}'.format(self.commit, self.netid)

    @property
    def netid(self):
        if self.student is not None:
            return self.student.netid
        return 'null'

    @property
    def json(self):
        return {
            'id': self.id,
            'netid': self.netid,
            'assignment': self.assignment.name,
            'url': self.url,
            'commit': self.commit,
            'processed': self.processed,
            'timestamp': str(self.timestamp),
        }


class Builds(db.Model):
    __tablename__ = 'builds'
    id = db.Column(db.Integer, primary_key=True)
    submissionid = db.Column(db.Integer, db.ForeignKey('submissions.id'), index=True)

    stdout=db.Column(db.Text)

    submission = db.relationship('Submissions', backref='builds')

    @property
    def json(self):
        return {
            'stdout': self.stdout,
        }


class Tests(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    submissionid = db.Column(db.Integer, db.ForeignKey('submissions.id'), index=True)

    stdout=db.Column(db.Text)

    submission = db.relationship('Submissions', backref='tests')

    @property
    def json(self):
        return {
            'stdout': self.stdout
        }


class Reports(db.Model):
    """
    Results
    """
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    submissionid = db.Column(db.Integer, db.ForeignKey('submissions.id'))
    testname = db.Column(db.String(128), index=True)
    errors = db.Column(db.Text)
    passed = db.Column(db.Boolean)

    submission = db.relationship('Submissions', backref='reports')

    @property
    def json(self):
        return {
            'testname': self.testname,
            'errors': self.errors,
            'passed': self.passed,
        }

    def __str__(self):
        return 'testname: {}\nerrors: {}\npassed: {}\n'.format(
            self.testname,
            self.errors,
            self.passed,
        )


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.Text, nullable=False, unique=True)
    due_date=db.Column(db.DateTime(True), nullable=False)
    grace_date=db.Column(db.DateTime(True), nullable=False)

    @property
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'due_date': str(self.due_date),
            'grace_date': str(self.grace_date),
        }


class Errors(db.Model):
    __tablename__ = 'errors'
    id = db.Column(db.Integer, primary_key=True)
    submissionid = db.Column(db.Integer, db.ForeignKey('submissions.id'), index=True)

    message=db.Column(db.Text)

    submission = db.relationship('Submissions', backref='errors')

    @property
    def json(self):
        return {
            'message': self.message,
        }
