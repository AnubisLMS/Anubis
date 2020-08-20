import hashlib
import logging
import random
import time
from datetime import datetime
from typing import Union

import jwt
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    netid = db.Column(db.String(128), unique=True, index=True)
    github_username = db.Column(db.String(128), index=True)
    name = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    @staticmethod
    def load_user(netid: Union[str, None]):
        """
        Load a user by username

        :param netid: netid of wanted user
        :return: User object or None
        """
        if netid is None:
            return None
        u1 = User.query.filter_by(netid=netid).first()

        logging.debug(f'loading user {u1.data}')

        return u1

    @staticmethod
    def current_user():
        """
        Load current user based on the token

        :return: User or None
        """
        token = request.headers.get('token', default=None)
        if token is None:
            return None

        try:
            # TODO update secret key
            decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
        except Exception as e:
            return None

        if 'netid' not in decoded:
            return None

        return User.load_user(decoded['netid'])

    @property
    def token(self):
        return jwt.encode({
            'netid': self.netid,
            # 'exp': datetime.utcnow() + timedelta(weeks=4),
            # TODO update secret key
        }, 'secret', algorithm='HS256').decode()

    @property
    def data(self):
        return {
            'id': self.id,
            'netid': self.netid,
            'github_username': self.github_username,
            'name': self.name,
            'admin': self.admin,
        }


class Assignment(db.Model):
    __tablename__ = 'assignment'
    id = db.Column(db.Integer, primary_key=True)
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


class AssignmentTest(db.Model):
    __tablename__ = 'assignment_test'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    name = db.Column(db.String(128), index=True)

    submission = db.relationship('Submission', cascade='all,delete', backref='test_results')


class AssignmentQuestion(db.Model):
    __tablename__ = 'assignment_question'
    id = db.Column(db.Integer, primary_key=True)
    assignemnt_id = db.Column(db.Integer, db.ForeignKey(Assignment.id), index=True)
    content = db.Column(db.Text, unique=True, nullable=False)
    solution = db.Column(db.Text, nullable=True)
    level = db.Column(db.Integer, index=True, nullable=False)

    assignment = db.relationship(Assignment, cascade='all,delete', backref='questions')

    @property
    def data(self):
        return {
            'id': self.id,
            'content': self.content,
            'solution': self.solution,
            'level': self.level
        }


class AssignmentStudentQuestion(db.Model):
    __tablename__ = 'student_question'
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey(Assignment.id), index=True, nullable=False)
    question1id = db.Column(db.Integer, db.ForeignKey('finalquestions.id'))
    question2id = db.Column(db.Integer, db.ForeignKey('finalquestions.id'))
    question3id = db.Column(db.Integer, db.ForeignKey('finalquestions.id'))
    question4id = db.Column(db.Integer, db.ForeignKey('finalquestions.id'))
    code = db.Column(db.Text, unique=True, nullable=False)

    student = db.relationship('Student', cascade='all,delete', backref='assignment_questions')

    @staticmethod
    def populate_codes():
        """
        Populate the student / code data for the StudentFinalQuestions table. This
        function should be used to seed inital student and code data to the table.
        Once this data is generated, there should never be any reason to modify it.
        Changing the student code in the middle of the exam will only cause confusion,
        so avoid it at all costs.

        The code will be the sha256 of the student netid, some nonce (timestamp) and
        some sufficiently random value (for each student).

        :return: boolean to indicate success
        """
        timestamp = time.time()
        sha256 = lambda s: hashlib.sha256(str(s).encode()).hexdigest()
        for student in User.query.all():
            netid = student.netid
            if AssignmentStudentQuestion.query.filter_by(studentid=student.id).first() is not None:
                # skip if student data already present
                continue
            code = sha256('{}{}{}'.format(
                netid,
                timestamp,
                random.getrandbits(100)
            ))
            sfq = AssignmentStudentQuestion(
                studentid=student.id,
                code=code
            )
            db.session.add(sfq)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return False
        return True

    @staticmethod
    def populate(overwrite=False):
        """
        Populate student final question data. We should call this every time we
        upload / add questions to the FinalQuestions table. The table entries should
        only ever be modified if they are not already populated. Otherwise we should
        skip. We will want to do this to avoid accidentally overwriting an existing
        students question bank. That would only cause confusion. You can optionally
        overwrite the data by specifying the overwrite argument to True. Use this
        with extreme caution.

        The StudentFinalQuestions table should already be populated with student data
        and the random codes when we go to populate the questions. We will call the
        populateCodes function every time, to ensure that that data is already there.
        (there is no effect with this function if the code data is already specified)

        response is dict of shape
        {
          success : bool
          error? : "..."
        }

        :param overwrite: bool to indicate if we should overwrite existing data
        :return: dict as specified above
        """
        if len(AssignmentStudentQuestion.query.all()) == 0:
            err = AssignmentStudentQuestion.populate_codes()
            if not err:
                return {
                    'success': False,
                    'error': 'failed to populate codes'
                }

        """
        questions: {
          level : [
            {
              id
              content
              answer
              level
            },
            ...
          ],
          ...
        }
        """
        questions = {
            level: list(map(
                lambda q: q.data,
                AssignmentQuestion.query.filter_by(level=level).all()
            ))
            for level in range(1, 5)
        }

        for sfq in AssignmentStudentQuestion.query.all():
            # don't overwrite existing student questions on accident
            if overwrite or not sfq.is_populated:
                sfq.question1id = random.choice(questions[1])['id']
                sfq.question2id = random.choice(questions[2])['id']
                sfq.question3id = random.choice(questions[3])['id']
                sfq.question4id = random.choice(questions[4])['id']
                db.session.add(sfq)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {
                'success': False,
                'error': 'unable to populate questions'
            }

        return {
            'success': True
        }

    @property
    def is_populated(self):
        """
        :return: true if questions are not populated
        """
        return self.question1id is not None \
               and self.question2id is not None \
               and self.question3id is not None \
               and self.question4id is not None

    @property
    def final_questions(self):
        """
        Reads, then gets final question objects based
        on the values of the foreign key fields.

        :return: list of Final question objects
        """
        return [
            AssignmentQuestion.query.filter_by(id=self.question1id).first(),
            AssignmentQuestion.query.filter_by(id=self.question2id).first(),
            AssignmentQuestion.query.filter_by(id=self.question3id).first(),
            AssignmentQuestion.query.filter_by(id=self.question4id).first(),
        ]

    @property
    def data(self):
        """
        Returns simple dictionary representation of the object.

        :return:
        """

        final_questions = list(sorted(
            map(
                lambda q: q.data,
                self.final_questions
            ),
            key=lambda question: question['level']
        )) if self.is_populated else []

        return {
            'questions': final_questions,
            'student': self.student.data,
            'code': self.code
        }


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

    student = db.relationship(User, cascade='all,delete', backref='submissions')
    assignment = db.relationship(Assignment, cascade='all,delete')

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
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey(Submission.id), index=True)

    stdout = db.Column(db.Text)

    submission = db.relationship('Submissions', cascade='all,delete', backref='build', uselist=False)

    @property
    def data(self):
        return {
            'stdout': self.stdout,
        }
