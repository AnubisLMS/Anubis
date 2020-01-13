from .app import db
from datetime import datetime


class Submissions(db.Model):
    """
    Submissions
    """
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    netid = db.Column(db.String(128), index=True)
    assignment = db.Column(db.Text, index=True)
    commit = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.now)


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


class Events(db.Model):
    """
    Events
    """
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    type = db.Column(db.String(128))
    message = db.Column(db.Text)
