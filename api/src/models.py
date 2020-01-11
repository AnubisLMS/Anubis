from .app import db
from datetime import datetime


class Submissions(db.Model):
    """
    Submissions
    """
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    netid = db.Column(db.String(128), index=True)
    grade = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.now)


class Results(db.Model):
    """
    Results
    """
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    submissionid = db.Column(db.Integer, db.ForeignKey('submissions.id'), index=True)
    stdout = db.Column(db.Text)
    errors = db.Column(db.Text)
    passed = db.Column(db.Boolean)

    submission = db.relationship('Submissions', backref='results')


class Events(db.Model):
    """
    Events
    """
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    type = db.Column(db.String(128))
    message = db.Column(db.Text)
