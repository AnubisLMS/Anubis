import base64
import logging
import os
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_json import MutableJson

db = SQLAlchemy()


class Config(db.Model):
    __tablename__ = 'config'
    key = db.Column(db.String(128), primary_key=True)
    value = db.Column(db.String(2048))


class User(db.Model):
    __tablename__ = 'user'

    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Fields
    netid = db.Column(db.String(128), primary_key=True, unique=True, index=True)
    github_username = db.Column(db.String(128), index=True)
    name = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    repos = db.relationship('AssignmentRepo', cascade='all,delete')
    in_class = db.relationship('InClass', cascade='all,delete')

    @property
    def data(self):
        return {
            'id': self.id,
            'netid': self.netid,
            'github_username': self.github_username,
            'name': self.name,
            'is_admin': self.is_admin,
        }


class Class_(db.Model):
    __tablename__ = '_class'

    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Fields
    name = db.Column(db.String(256), nullable=False)
    class_code = db.Column(db.String(256), nullable=False)
    section = db.Column(db.String(256), nullable=True)
    professor = db.Column(db.String(256), nullable=False)

    in_class = db.relationship('InClass', cascade='all,delete')

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

    owner = db.relationship(User, cascade='all,delete')
    class_ = db.relationship(Class_, cascade='all,delete')


class Assignment(db.Model):
    __tablename__ = 'assignment'

    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    class_id = db.Column(db.Integer, db.ForeignKey(Class_.id), index=True)

    # Fields
    name = db.Column(db.String(256), nullable=False, unique=True)
    hidden = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=True)
    github_classroom_url = db.Column(db.String(256), nullable=True)
    pipeline_image = db.Column(db.String(256), unique=True, nullable=True)
    unique_code = db.Column(db.String(8), unique=True, default=lambda: base64.b16encode(os.urandom(4)).decode())

    # Dates
    release_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    grace_date = db.Column(db.DateTime, nullable=True)

    class_ = db.relationship(Class_, cascade='all,delete', backref='assignments')
    tests = db.relationship('AssignmentTest', cascade='all,delete')
    repos = db.relationship('AssignmentRepo', cascade='all,delete')

    @property
    def data(self):
        return {
            'id': self.id,
            'name': self.name,
            'due_date': str(self.due_date),
            'grace_date': str(self.grace_date),
            'class': self.class_.data,
            'description': self.description,
            'github_classroom_link': self.github_classroom_url,

            'tests': [t.data for t in self.tests]
        }

    @property
    def meta_shape(self):
        return {
            'assignment': {
                "name": str,
                "class": str,
                "unique_code": str,
                "hidden": bool,
                "github_classroom_url": str,
                "pipeline_image": str,
                "release_date": str,
                "due_date": str,
                "grace_date": str,
                "description": str,
            }
        }


class AssignmentRepo(db.Model):
    __tablename__ = 'assignment_repo'

    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey(Assignment.id), nullable=False)

    repo_url = db.Column(db.String(128), nullable=False)

    # Relationships
    owner = db.relationship(User, cascade='all,delete')
    assignment = db.relationship(Assignment, cascade='all,delete')
    submissions = db.relationship('Submission', cascade='all,delete')


class AssignmentTest(db.Model):
    __tablename__ = 'assignment_test'

    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    assignment_id = db.Column(db.Integer, db.ForeignKey(Assignment.id))

    # Fields
    name = db.Column(db.String(128), index=True)

    # Relationships
    assignment = db.relationship(Assignment, cascade='all,delete')

    @property
    def data(self):
        return {
            'name': self.name
        }


class AssignmentQuestion(db.Model):
    __tablename__ = 'assignment_question'

    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    assignment_id = db.Column(db.Integer, db.ForeignKey(Assignment.id), index=True)

    # Fields
    content = db.Column(db.Text, nullable=False)
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

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
    __tablename__ = 'submission'

    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id), index=True, nullable=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey(Assignment.id), index=True, nullable=False)
    assignment_repo_id = db.Column(db.Integer, db.ForeignKey(AssignmentRepo.id), nullable=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Fields
    commit = db.Column(db.String(128), unique=True, index=True, nullable=False)
    processed = db.Column(db.Boolean, default=False)
    state = db.Column(db.String(128), default='')
    errors = db.Column(MutableJson, default=None, nullable=True)
    token = db.Column(db.String(64), default=lambda: base64.b16encode(os.urandom(32)).decode())

    # Relationships
    owner = db.relationship(User, cascade='all,delete')
    assignment = db.relationship(Assignment, cascade='all,delete')
    build = db.relationship('SubmissionBuild', cascade='all,delete', uselist=False)
    test_results = db.relationship('SubmissionTestResult', cascade='all,delete')
    repo = db.relationship(AssignmentRepo, cascade='all,delete')

    def init_submission_models(self):
        """
        Create adjacent submission models.

        :return:
        """
        # If the models already exist, yeet
        if len(self.test_results) != 0:
            SubmissionTestResult.query.filter_by(submission_id=self.id).delete()
        if self.build is not None:
            SubmissionBuild.query.filter_by(submission_id=self.id).delete()

        # Commit deletions (if necessary)
        db.session.commit()

        # Find tests for the current assignment
        tests = AssignmentTest.query.filter(Assignment.id == self.assignment_id).all()

        logging.debug('found tests: {}'.format(list(map(lambda x: x.data, tests))))

        for test in tests:
            tr = SubmissionTestResult(submission=self, assignment_test=test)
            db.session.add(tr)
        sb = SubmissionBuild(submission=self)
        db.session.add(sb)

        # Commit new models
        db.session.commit()

    @property
    def url(self):
        return 'https://anubis.osiris.services/submission/{}'.format(self.commit)

    @property
    def netid(self):
        if self.owner is not None:
            return self.owner.netid
        return 'null'

    @property
    def tests(self):
        """
        Get a list of dictionaries of the matching Test, and TestResult
        for the current submission.

        :return:
        """

        # Query for matching AssignmentTests, and TestResults
        tests = db.session.query(
            AssignmentTest, SubmissionTestResult
        ).join(Assignment).join(Class_).join(InClass).join(User).join(Submission).filter(
            Assignment.id == self.assignment_id,
            User.id == self.owner_id,
            SubmissionTestResult.submission_id == Submission.id,
            SubmissionTestResult.assignment_test_id == AssignmentTest.id,
        ).group_by(AssignmentTest.id).all()
        # ^^ Dont Touch this ^^

        logging.debug('Loaded tests {}'.format(tests))

        # Convert to dictionary data
        return [
            {'test': test.data, 'result': result.data}
            for test, result in tests
        ]

    @property
    def data(self):
        return {
            'id': self.id,
            'netid': self.netid,
            'assignment': self.assignment.name,
            'url': self.url,
            'commit': self.commit,
            'processed': self.processed,
            'state': self.state,
            'created': str(self.created),
            'last_updated': str(self.last_updated),

            # Connected models
            'repo': self.repo.repo_url,
            'tests': self.tests,
            'submission_build': self.build.data if self.build is not None else None,
        }


class SubmissionTestResult(db.Model):
    __tablename__ = 'submission_test_result'

    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    submission_id = db.Column(db.Integer, db.ForeignKey(Submission.id), primary_key=True)
    assignment_test_id = db.Column(db.Integer, db.ForeignKey(AssignmentTest.id), primary_key=True)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Fields
    stdout = db.Column(db.Text)
    message = db.Column(db.Text)
    passed = db.Column(db.Boolean)

    # Relationships
    submission = db.relationship(Submission, cascade='all,delete')
    assignment_test = db.relationship(AssignmentTest, cascade='all,delete')

    @property
    def data(self):
        return {
            'test_name': self.assignment_test.name,
            'passed': self.passed,
            'message': self.message,
            'stdout': self.stdout,
            'created': str(self.created),
            'last_updated': str(self.last_updated),
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    submission_id = db.Column(db.Integer, db.ForeignKey(Submission.id), index=True)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Fields
    stdout = db.Column(db.Text)
    passed = db.Column(db.Boolean)

    # Relationships
    submission = db.relationship(Submission, cascade='all,delete')

    @property
    def data(self):
        return {
            'stdout': self.stdout,
            'passed': self.passed,
        }
