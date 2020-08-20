from datetime import datetime, timedelta

import jwt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_json import MutableJson
from anubis.config import Config
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    # id
    id = db.Column(db.Integer, primary_key=True)

    # Fields
    netid = db.Column(db.String(128), primary_key=True, unique=True, index=True)
    github_username = db.Column(db.String(128), index=True)
    name = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def classes(self):
        return [
            in_class.class_
            for in_class in self.in_classes
        ]

    @property
    def token(self):
        return jwt.encode({
            'netid': self.netid,
            'exp': datetime.utcnow() + timedelta(hours=6),
        }, Config.SECRET_KEY, algorithm='HS256').decode()

    @property
    def data(self):
        return {
            'id': self.id,
            'netid': self.netid,
            'github_username': self.github_username,
            'name': self.name,
            'admin': self.admin,
        }


class Class_(db.Model):
    __tablename__ = '_class'

    # id
    id = db.Column(db.Integer, primary_key=True)

    # Fields
    name = db.Column(db.String(256), nullable=False)
    class_code = db.Column(db.String(256), nullable=False)
    section = db.Column(db.String(256), nullable=True)
    professor = db.Column(db.String(256), nullable=False)

    @property
    def data(self):
        return {
            'name': self.name,
            'class_code': self.class_code,
            'section': self.section,
            'professor': self.professor,
        }


class InClass(db.Model):
    __tablename__ = 'in_class'

    # Foreign Keys
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey(Class_.id), primary_key=True)

    owner = db.relationship(User, cascade='all,delete', backref='in_class')
    class_ = db.relationship(Class_, cascade='all,delete', backref='students')


class Assignment(db.Model):
    __tablename__ = 'assignment'

    # id
    id = db.Column(db.Integer, primary_key=True)

    # Fields
    name = db.Column(db.Text, nullable=False, unique=True)
    due_date = db.Column(db.DateTime(True), nullable=False)
    grace_date = db.Column(db.DateTime(True), nullable=False)

    @property
    def data(self):
        return {
            'id': self.id,
            'name': self.name,
            'due_date': str(self.due_date),
            'grace_date': str(self.grace_date),
        }


class AssignmentRepo(db.Model):
    __tablename__ = 'assignment_repo'

    # id
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey(Assignment.id), nullable=False)

    # Relationships
    owner = db.relationship(User, cascade='all,delete', backref='submissions')
    assignment = db.relationship(Assignment, cascade='all,delete')


class AssignmentTest(db.Model):
    __tablename__ = 'assignment_test'

    # id
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))

    # Fields
    name = db.Column(db.String(128), index=True)

    # Relationships
    submission = db.relationship('Submission', cascade='all,delete', backref='test_results')


class AssignmentQuestion(db.Model):
    __tablename__ = 'assignment_question'

    # id
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    assignment_id = db.Column(db.Integer, db.ForeignKey(Assignment.id), index=True)

    # Fields
    content = db.Column(db.Text, unique=True, nullable=False)
    solution = db.Column(db.Text, nullable=True)
    level = db.Column(db.Integer, index=True, nullable=False)

    # Relationships
    assignment = db.relationship(Assignment, cascade='all,delete', backref='questions')

    @property
    def data(self):
        return {
            'id': self.id,
            'content': self.content,
            'solution': self.solution,
            'level': self.level
        }


class AssignedStudentQuestion(db.Model):
    __tablename__ = 'assigned_student_question'

    # id
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id))
    assignment_id = db.Column(db.Integer, db.ForeignKey(Assignment.id), index=True, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey(AssignmentQuestion.id), index=True, nullable=False)

    # Relationships
    owner = db.relationship(User, cascade='all,delete')
    assignment = db.relationship(Assignment, cascade='all,delete')
    question = db.relationship(AssignmentQuestion, cascade='all,delete')

    @property
    def data(self):
        """
        Returns simple dictionary representation of the object.

        :return:
        """

        return {
            'question': self.owner.data,
            'student': self.student.data,
            'assignment': self.assignment.data
        }


class Submission(db.Model):
    __tablename__ = 'submissions'

    # id
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id), index=True, nullable=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey(Assignment.id), index=True, nullable=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Fields
    commit = db.Column(db.String(128), unique=True, index=True, nullable=False)
    processed = db.Column(db.Boolean, default=False)
    errors = db.Column(MutableJson, default=None, nullable=True)

    # Relationships
    owner = db.relationship(User, cascade='all,delete', backref='submissions')
    assignment = db.relationship(Assignment, cascade='all,delete')

    @property
    def url(self):
        return 'https://anubis.osiris.services/view/{}/{}'.format(self.commit, self.netid)

    @property
    def netid(self):
        if self.owner is not None:
            return self.owner.netid
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

    # id
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    submission_id = db.Column(db.Integer, db.ForeignKey(Submission.id), primary_key=True)
    assignment_test_id = db.Column(db.Integer, db.ForeignKey(Submission.id), primary_key=True)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Fields
    stdout = db.Column(db.Text)
    errors = db.Column(db.Text)
    passed = db.Column(db.Boolean)

    # Relationships
    submission = db.relationship(Submission, cascade='all,delete', backref='test_results')
    assignment_test = db.relationship(AssignmentTest, cascade='all,delete', backref='test_results')

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

    # id
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    submission_id = db.Column(db.Integer, db.ForeignKey(Submission.id), index=True)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Fields
    stdout = db.Column(db.Text)

    # Relationships
    submission = db.relationship('Submissions', cascade='all,delete', backref='build', uselist=False)

    @property
    def data(self):
        return {
            'stdout': self.stdout,
        }
