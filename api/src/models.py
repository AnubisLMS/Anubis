import hashlib
import random
import time
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from .app import db


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

    stdout = db.Column(db.Text)

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

    stdout = db.Column(db.Text)

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    due_date = db.Column(db.DateTime(True), nullable=False)
    grace_date = db.Column(db.DateTime(True), nullable=False)

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

    message = db.Column(db.Text)

    submission = db.relationship('Submissions', backref='errors')

    @property
    def json(self):
        return {
            'message': self.message,
        }


class FinalQuestions(db.Model):
    __tablename__ = 'finalquestions'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, unique=True, nullable=False)
    solution = db.Column(db.Text, nullable=True)
    level = db.Column(db.Integer, index=True, nullable=False)

    @property
    def json(self):
        return {
            'id': self.id,
            'content': self.content,
            'solution': self.solution,
            'level': self.level
        }


class StudentFinalQuestions(db.Model):
    studentid = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    question1id = db.Column(db.Integer, db.ForeignKey('finalquestions.id'))
    question2id = db.Column(db.Integer, db.ForeignKey('finalquestions.id'))
    question3id = db.Column(db.Integer, db.ForeignKey('finalquestions.id'))
    question4id = db.Column(db.Integer, db.ForeignKey('finalquestions.id'))
    code = db.Column(db.Text, unique=True, nullable=False)

    student = db.relationship('Student', backref='finalquestions')

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
        for student in Student.query.all():
            netid = student.netid
            if StudentFinalQuestions.query.filter_by(studentid=student.id).first() is not None:
                # skip if student data already present
                continue
            code = sha256('{}{}{}'.format(
                netid,
                timestamp,
                random.getrandbits(100)
            ))
            sfq = StudentFinalQuestions(
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
        if len(StudentFinalQuestions.query.all()) == 0:
            err = StudentFinalQuestions.populate_codes()
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
                lambda q: q.json,
                FinalQuestions.query.filter_by(level=level).all()
            ))
            for level in range(1, 5)
        }

        for sfq in StudentFinalQuestions.query.all():
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
            FinalQuestions.query.filter_by(id=self.question1id).first(),
            FinalQuestions.query.filter_by(id=self.question2id).first(),
            FinalQuestions.query.filter_by(id=self.question3id).first(),
            FinalQuestions.query.filter_by(id=self.question4id).first(),
        ]

    @property
    def json(self):
        """
        Returns simple dictionary representation of the object.

        :return:
        """

        final_questions = list(sorted(
            map(
                lambda q: q.json,
                self.final_questions
            ),
            key=lambda question: question['level']
        )) if self.is_populated else []

        return {
            'questions': final_questions,
            'student': self.student.json,
            'code': self.code
        }
