import hashlib
import random
import time

from sqlalchemy.exc import IntegrityError

from .user import User
from .submission import Submission
from ..app import db


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
    submission_id = db.Column(db.Integer, db.ForeignKey(Submission.id))
    name = db.Column(db.String(128), index=True)


class AssignmentQuestion(db.Model):
    __tablename__ = 'assignment_question'
    id = db.Column(db.Integer, primary_key=True)
    assignemnt_id = db.Column(db.Integer, db.ForeignKey(Assignment.id), index=True)
    content = db.Column(db.Text, unique=True, nullable=False)
    solution = db.Column(db.Text, nullable=True)
    level = db.Column(db.Integer, index=True, nullable=False)

    assignment = db.relationship(Assignment, backref='questions')

    @property
    def data(self):
        return {
            'id': self.id,
            'content': self.content,
            'solution': self.solution,
            'level': self.level
        }


class StudentQuestion(db.Model):
    __tablename__ = 'student_question'
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
    question1id = db.Column(db.Integer, db.ForeignKey('finalquestions.id'))
    question2id = db.Column(db.Integer, db.ForeignKey('finalquestions.id'))
    question3id = db.Column(db.Integer, db.ForeignKey('finalquestions.id'))
    question4id = db.Column(db.Integer, db.ForeignKey('finalquestions.id'))
    code = db.Column(db.Text, unique=True, nullable=False)

    student = db.relationship('Student', backref='assignment_questions')

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
            if StudentQuestion.query.filter_by(studentid=student.id).first() is not None:
                # skip if student data already present
                continue
            code = sha256('{}{}{}'.format(
                netid,
                timestamp,
                random.getrandbits(100)
            ))
            sfq = StudentQuestion(
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
        if len(StudentQuestion.query.all()) == 0:
            err = StudentQuestion.populate_codes()
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

        for sfq in StudentQuestion.query.all():
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
