from .app import db
from datetime import datetime
import json

class Submissions(db.Model):
    """
    Submissions
    """
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    netid = db.Column(db.String(128), index=True)
    assignment = db.Column(db.Text, index=True)
    commit = db.Column(db.String(128))
    processed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    @property
    def json(self):
        return {
            'id': self.id,
            'netid': self.netid,
            'assignment': self.assignment,
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


class Tests(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    submissionid = db.Column(db.Integer, db.ForeignKey('submissions.id'), index=True)

    stdout=db.Column(db.Text)

    submission = db.relationship('Submissions', backref='tests')


class Reports(db.Model):
    """
    Results
    """
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    submissionid = db.Column(db.Integer, db.ForeignKey('submissions.id'))
    testname = db.Column(db.String(128), index=True)
    stdout = db.Column(db.Text)
    errors = db.Column(db.Text)
    passed = db.Column(db.Boolean)

    submission = db.relationship('Submissions', backref='reports')

    @property
    def json(self):
        return {
            'testname': self.testname,
            'stdout': self.stdout,
            'errors': self.errors,
            'passed': self.passed,
        }

    def __str__(self):
        return '{}:\n\nlogs:\n{}\n\nerrors:\n{}\n\npassed: {}\n'.format(
            self.testname,
            self.stdout,
            self.errors,
            self.passed,
        )


class Events(db.Model):
    """
    Events
    """
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    type = db.Column(db.String(128))
    message = db.Column(db.Text)
