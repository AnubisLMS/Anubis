import base64
import json
import os
from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import deferred
from sqlalchemy_json import MutableJson

from anubis.utils.data import rand

db = SQLAlchemy()


def default_id(max_len=None) -> db.Column:
    return db.Column(
        db.String(128), primary_key=True, default=lambda: rand(max_len or 32)
    )


class Config(db.Model):
    __tablename__ = "config"

    # Fields
    key = db.Column(db.String(128), primary_key=True)
    value = db.Column(db.String(2048))

    @property
    def data(self):
        return {
            'key': self.key,
            'value': self.value,
        }


class User(db.Model):
    __tablename__ = "user"

    # id
    id = default_id()

    # Fields
    netid = db.Column(db.String(128), primary_key=True, unique=True, index=True)
    github_username = db.Column(db.TEXT, index=True)
    name = db.Column(db.TEXT)
    is_superuser = db.Column(db.Boolean, nullable=False, default=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        professor_for = [pf.data for pf in self.professor_for]
        ta_for = [taf.data for taf in self.ta_for]
        super_for = None
        if self.is_superuser:
            super_for = []
            courses = Course.query.all()
            for course in courses:
                super_for.append({'id': course.id, 'name': course.name})
        return {
            "id": self.id,
            "netid": self.netid,
            "github_username": self.github_username,
            "name": self.name,
            "is_superuser": self.is_superuser,
            "is_admin": len(professor_for) > 0 or len(ta_for) > 0 or self.is_superuser,
            "professor_for": professor_for,
            "ta_for": ta_for,
            "admin_for": super_for or (professor_for + ta_for),
        }

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'<User {self.netid} {self.github_username}>'


class Course(db.Model):
    __tablename__ = "course"

    # id
    id = default_id()

    # Fields
    name = db.Column(db.TEXT, nullable=False)
    course_code = db.Column(db.TEXT, nullable=False)
    semester = db.Column(db.TEXT, nullable=True)
    section = db.Column(db.TEXT, nullable=True)
    professor = db.Column(db.TEXT, nullable=False)
    autograde_tests_repo = db.Column(db.TEXT, nullable=False,
                                     default='https://github.com/os3224/anubis-assignment-tests')
    theia_default_image = db.Column(db.TEXT, nullable=False, default='registry.digitalocean.com/anubis/xv6')
    theia_default_options = db.Column(MutableJson, default=lambda: {"limits": {"cpu": "2", "memory": "500Mi"}})
    github_org_url = db.Column(db.TEXT, default='')
    join_code = db.Column(db.String(256), unique=True)

    @property
    def total_assignments(self):
        return self.open_assignments

    @property
    def open_assignments(self):
        now = datetime.now()
        return Assignment.query.filter(
            Assignment.course_id == self.id,
            Assignment.release_date <= now,
            Assignment.hidden == False,
        ).count()

    @property
    def data(self):
        return {
            "id": self.id,
            "name": self.name,
            "course_code": self.course_code,
            "section": self.section,
            "professor": self.professor,
            "total_assignments": self.total_assignments,
            "open_assignment": self.open_assignments,
            "join_code": self.id[:6],
        }


class TAForCourse(db.Model):
    __tablename__ = "ta_for_course"

    # Foreign Keys
    owner_id = db.Column(db.String(128), db.ForeignKey(User.id), primary_key=True)
    course_id = db.Column(db.String(128), db.ForeignKey(Course.id), primary_key=True)

    owner = db.relationship(User, backref='ta_for')
    course = db.relationship(Course)

    @property
    def data(self):
        return {
            'id': self.course.id,
            'name': self.course.name,
        }


class ProfessorForCourse(db.Model):
    __tablename__ = "professor_for_course"

    # Foreign Keys
    owner_id = db.Column(db.String(128), db.ForeignKey(User.id), primary_key=True)
    course_id = db.Column(db.String(128), db.ForeignKey(Course.id), primary_key=True)

    owner = db.relationship(User, backref='professor_for')
    course = db.relationship(Course)

    @property
    def data(self):
        return {
            'id': self.course.id,
            'name': self.course.name,
        }


class InCourse(db.Model):
    __tablename__ = "in_course"

    # Foreign Keys
    owner_id = db.Column(db.String(128), db.ForeignKey(User.id), primary_key=True)
    course_id = db.Column(db.String(128), db.ForeignKey(Course.id), primary_key=True)

    owner = db.relationship(User)
    course = db.relationship(Course)


class Assignment(db.Model):
    __tablename__ = "assignment"

    # id
    id = default_id()

    # Foreign Keys
    course_id = db.Column(db.String(128), db.ForeignKey(Course.id), index=True)

    # Fields
    name = db.Column(db.TEXT, nullable=False, index=True)
    hidden = db.Column(db.Boolean, default=False)
    description = db.Column(db.TEXT, nullable=True)
    github_classroom_url = db.Column(db.TEXT, nullable=True, default=None)
    pipeline_image = db.Column(db.TEXT, nullable=True, index=True)
    unique_code = db.Column(
        db.String(8),
        unique=True,
        default=lambda: base64.b16encode(os.urandom(4)).decode(),
    )
    ide_enabled = db.Column(db.Boolean, default=True)
    accept_late = db.Column(db.Boolean, default=True)
    autograde_enabled = db.Column(db.Boolean, default=True)
    theia_image = db.Column(
        db.TEXT, default="registry.digitalocean.com/anubis/theia-xv6"
    )
    theia_options = db.Column(MutableJson, default=lambda: {})

    # Dates
    release_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    grace_date = db.Column(db.DateTime, nullable=True)

    course = db.relationship(Course, backref="assignments")
    tests = db.relationship("AssignmentTest", cascade="all,delete", backref='assignment')
    repos = db.relationship("AssignmentRepo", cascade="all,delete", backref='assignment')

    @property
    def data(self):
        from anubis.utils.lms.assignments import get_assignment_due_date
        from anubis.utils.auth import current_user

        due_date = get_assignment_due_date(current_user(), self)

        return {
            "id": self.id,
            "name": self.name,
            "due_date": str(due_date),
            "past_due": due_date < datetime.now(),
            "hidden": self.hidden,
            "accept_late": self.accept_late,
            "course": self.course.data,
            "description": self.description,
            "ide_enabled": self.ide_enabled,
            "autograde_enabled": self.autograde_enabled,
            "ide_active": self.due_date + timedelta(days=3 * 7) > datetime.now(),
            "github_classroom_link": self.github_classroom_url,
            "tests": [t.data for t in self.tests if t.hidden is False],
        }

    @property
    def full_data(self):
        data = self.data
        data['tests'] = [t.data for t in self.tests]
        return data

    @property
    def meta_shape(self):
        return {
            "assignment": {
                "name": str,
                "course": str,
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
    __tablename__ = "assignment_repo"

    # id
    id = default_id()

    # Foreign Keys
    owner_id = db.Column(db.String(128), db.ForeignKey(User.id), nullable=True)
    assignment_id = db.Column(
        db.String(128), db.ForeignKey(Assignment.id), nullable=False
    )

    # Fields
    github_username = db.Column(db.TEXT, nullable=False)
    repo_url = db.Column(db.TEXT, nullable=False)

    # Relationships
    owner = db.relationship(User)

    @property
    def data(self):
        return {
            "id": self.id,
            "github_username": self.github_username,
            "assignment_name": self.assignment.name,
            "course_code": self.assignment.course.course_code,
            "repo_url": self.repo_url,
        }


class AssignmentTest(db.Model):
    __tablename__ = "assignment_test"

    # id
    id = default_id()

    # Foreign Keys
    assignment_id = db.Column(db.String(128), db.ForeignKey(Assignment.id))

    # Fields
    name = db.Column(db.TEXT, index=True)
    hidden = db.Column(db.Boolean, default=False)

    @property
    def data(self):
        return {
            "id": self.id,
            "name": self.name,
            "hidden": self.hidden
        }


class AssignmentQuestion(db.Model):
    __tablename__ = "assignment_question"

    # id
    id = default_id()

    # Foreign Keys
    assignment_id = db.Column(db.String(128), db.ForeignKey(Assignment.id), index=True)

    # Fields
    question = db.Column(db.Text, nullable=False)
    solution = db.Column(db.Text, nullable=True)
    pool = db.Column(db.Integer, index=True, nullable=False)
    code_question = db.Column(db.Boolean, default=False)
    code_language = db.Column(db.TEXT, nullable=True, default='')
    placeholder = db.Column(db.Text, nullable=True, default="")

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    assignment = db.relationship(Assignment, backref="questions")

    shape = {"question": str, "solution": str, "pool": int}

    @property
    def full_data(self):
        return {
            "id": self.id,
            "question": self.question,
            "code_question": self.code_question,
            "code_language": self.code_language,
            "solution": self.solution,
            "pool": self.pool,
        }

    @property
    def data(self):
        return {
            "id": self.id,
            "question": self.question,
            "code_question": self.code_question,
            "code_language": self.code_language,
            "pool": self.pool,
        }


class AssignedStudentQuestion(db.Model):
    __tablename__ = "assigned_student_question"

    # id
    id = default_id()

    # Foreign Keys
    owner_id = db.Column(db.String(128), db.ForeignKey(User.id))
    assignment_id = db.Column(
        db.String(128), db.ForeignKey(Assignment.id), index=True, nullable=False
    )
    question_id = db.Column(
        db.String(128), db.ForeignKey(AssignmentQuestion.id), index=True, nullable=False
    )

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    owner = db.relationship(User)
    assignment = db.relationship(Assignment)
    question = db.relationship(AssignmentQuestion)
    responses = db.relationship('AssignedQuestionResponse', cascade='all,delete', backref='question')

    @property
    def data(self):
        """
        Returns simple dictionary representation of the object.

        :return:
        """

        response: AssignedQuestionResponse = AssignedQuestionResponse.query.filter(
            AssignedQuestionResponse.assigned_question_id == self.id,
        ).order_by(AssignedQuestionResponse.created.desc()).first()

        response_data = {'submitted': None, 'late': True, 'text': self.question.placeholder}
        if response is not None:
            response_data = response.data

        return {
            "id": self.id,
            "response": response_data,
            "question": self.question.data,
        }

    @property
    def full_data(self):
        data = self.data
        data['question'] = self.question.full_data
        return data


class AssignedQuestionResponse(db.Model):
    __tablename__ = "assigned_student_response"

    # id
    id = default_id()

    # Foreign Keys
    assigned_question_id = db.Column(
        db.String(128), db.ForeignKey(AssignedStudentQuestion.id), index=True, nullable=False
    )

    # Fields
    response = db.Column(db.TEXT, default='', nullable=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        from anubis.utils.lms.assignments import get_assignment_due_date

        return {
            'submitted': str(self.created),
            'late': get_assignment_due_date(self.question.owner, self.question.assignment) < self.created,
            'text': self.response,
        }


class Submission(db.Model):
    __tablename__ = "submission"

    # id
    id = default_id()

    # Foreign Keys
    owner_id = db.Column(
        db.String(128), db.ForeignKey(User.id), index=True, nullable=True
    )
    assignment_id = db.Column(
        db.String(128), db.ForeignKey(Assignment.id), index=True, nullable=False
    )
    assignment_repo_id = db.Column(
        db.String(128), db.ForeignKey(AssignmentRepo.id), nullable=False
    )

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Fields
    commit = db.Column(db.String(128), unique=True, index=True, nullable=False)
    processed = db.Column(db.Boolean, default=False)
    state = db.Column(db.TEXT, default="")
    errors = db.Column(MutableJson, default=None, nullable=True)
    token = db.Column(
        db.String(64), default=lambda: base64.b16encode(os.urandom(32)).decode()
    )
    accepted = db.Column(db.Boolean, default=True)

    # Relationships
    owner = db.relationship(User)
    assignment = db.relationship(Assignment)
    build = db.relationship("SubmissionBuild", cascade="all,delete", uselist=False, backref='submission')
    test_results = db.relationship("SubmissionTestResult", cascade="all,delete", backref='submission')
    repo = db.relationship(AssignmentRepo, backref='submissions')

    @property
    def netid(self):
        if self.owner is not None:
            return self.owner.netid
        return "null"

    @property
    def visible_tests(self):
        """
        Get a list of dictionaries of the matching Test, and TestResult
        for the current submission.

        :return:
        """

        # Query for matching AssignmentTests, and TestResults
        tests = SubmissionTestResult.query.join(AssignmentTest).filter(
            SubmissionTestResult.submission_id == self.id,
            AssignmentTest.hidden == False,
        ).all()

        # Convert to dictionary data
        return [
            {"test": result.assignment_test.data, "result": result.data}
            for result in tests
        ]

    @property
    def all_tests(self):
        """
        Get a list of dictionaries of the matching Test, and TestResult
        for the current submission.

        :return:
        """

        # Query for matching AssignmentTests, and TestResults
        tests = SubmissionTestResult.query.join(AssignmentTest).filter(
            SubmissionTestResult.submission_id == self.id,
        ).all()

        # Convert to dictionary data
        return [
            {"test": result.assignment_test.data, "result": result.data}
            for result in tests
        ]

    @property
    def data(self):
        return {
            "id": self.id,
            "assignment_name": self.assignment.name,
            "assignment_due": str(self.assignment.due_date),
            "course_code": self.assignment.course.course_code,
            "commit": self.commit,
            "processed": self.processed,
            "state": self.state,
            "created": str(self.created),
            "last_updated": str(self.last_updated),
            "error": self.errors is not None,
        }

    @property
    def full_data(self):
        data = self.data

        # Add connected models
        data["repo"] = self.repo.repo_url
        data["tests"] = self.visible_tests
        data["build"] = self.build.data if self.build is not None else None

        return data

    @property
    def admin_data(self):
        data = self.data

        # Add connected models
        data["repo"] = self.repo.repo_url
        data["tests"] = self.all_tests
        data["build"] = self.build.data if self.build is not None else None

        return data


class SubmissionTestResult(db.Model):
    __tablename__ = "submission_test_result"

    # id
    id = default_id()

    # Foreign Keys
    submission_id = db.Column(
        db.String(128), db.ForeignKey(Submission.id), primary_key=True
    )
    assignment_test_id = db.Column(
        db.String(128), db.ForeignKey(AssignmentTest.id), primary_key=True
    )

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Fields
    stdout = deferred(db.Column(db.Text))
    message = deferred(db.Column(db.Text))
    passed = db.Column(db.Boolean)

    # Relationships
    assignment_test = db.relationship(AssignmentTest)

    @property
    def data(self):
        return {
            "id": self.id,
            "test_name": self.assignment_test.name,
            "passed": self.passed,
            "message": self.message,
            "stdout": self.stdout,
            "created": str(self.created),
            "last_updated": str(self.last_updated),
        }

    @property
    def stat_data(self):
        data = self.data
        del data["stdout"]
        return data

    def __str__(self):
        return "testname: {}\nerrors: {}\npassed: {}\n".format(
            self.testname,
            self.errors,
            self.passed,
        )


class SubmissionBuild(db.Model):
    __tablename__ = "submission_build"

    # id
    id = default_id()

    # Foreign Keys
    submission_id = db.Column(db.String(128), db.ForeignKey(Submission.id), index=True)

    # Fields
    stdout = deferred(db.Column(db.Text))
    passed = db.Column(db.Boolean, default=None)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        return {
            "stdout": self.stdout,
            "passed": self.passed,
        }

    @property
    def stat_data(self):
        data = self.data
        del data["stdout"]
        return data


class TheiaSession(db.Model):
    __tablename__ = "theia_session"

    # id
    id = default_id(32)
    course_id = db.Column(db.String(128), db.ForeignKey(Course.id), nullable=False, index=True)

    # Foreign keys
    owner_id = db.Column(db.String(128), db.ForeignKey(User.id), nullable=False)
    assignment_id = db.Column(
        db.String(128), db.ForeignKey(Assignment.id), nullable=True
    )
    repo_url = db.Column(db.String(128), nullable=False)

    # Fields
    active = db.Column(db.Boolean, default=True)
    state = db.Column(db.TEXT)
    cluster_address = db.Column(db.TEXT, nullable=True, default=None)
    image = db.Column(
        db.TEXT, default="registry.digitalocean.com/anubis/theia-xv6"
    )
    options = db.Column(MutableJson, nullable=False, default=lambda: dict())
    network_locked = db.Column(db.Boolean, default=True)
    privileged = db.Column(db.Boolean, default=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    ended = db.Column(db.DateTime, nullable=True, default=None)
    last_heartbeat = db.Column(db.DateTime, default=datetime.now)
    last_proxy = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    owner = db.relationship(User)
    assignment = db.relationship(Assignment)
    course = db.relationship(Course)

    @property
    def data(self):
        from anubis.utils.lms.theia import theia_redirect_url

        return {
            "id": self.id,
            "assignment_id": self.assignment_id,
            "assignment_name": self.assignment.name
            if self.assignment_id is not None
            else None,
            "course_code": self.assignment.course.course_code
            if self.assignment_id is not None
            else None,
            "netid": self.owner.netid,
            "repo_url": self.repo_url,
            "redirect_url": theia_redirect_url(self.id, self.owner.netid),
            "active": self.active,
            "state": self.state,
            "created": str(self.created),
            "ended": str(self.ended),
            "last_heartbeat": str(self.last_heartbeat),
            "last_proxy": str(self.last_proxy),
            "last_updated": str(self.last_updated),
            "autosave": self.options.get('autosave', True),
        }

    @property
    def settings(self):
        return {
            'image': self.image,
            'repo_url': self.repo_url,
            'options': json.dumps(self.options),
            'privileged': self.privileged,
            'network_locked': self.network_locked
        }


class StaticFile(db.Model):
    __tablename__ = "static_file"

    id = default_id()
    course_id = db.Column(db.String(128), db.ForeignKey(Course.id), nullable=False, index=True)

    # Fields
    filename = db.Column(db.TEXT)
    path = db.Column(db.TEXT)
    content_type = db.Column(db.TEXT)
    blob = deferred(db.Column(db.LargeBinary(length=(2 ** 32) - 1)))
    hidden = db.Column(db.Boolean)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    course = db.relationship(Course)

    @property
    def data(self):
        return {
            "id": self.id,
            "content_type": self.content_type,
            "filename": self.filename,
            "path": self.path,
            "hidden": self.hidden,
            "uploaded": str(self.created)
        }


class LateException(db.Model):
    user_id = db.Column(db.String(128), db.ForeignKey(User.id), primary_key=True)
    assignment_id = db.Column(db.String(128), db.ForeignKey(Assignment.id), primary_key=True)

    # New Due Date
    due_date = db.Column(db.DateTime, nullable=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    assignment = db.relationship(Assignment)
    user = db.relationship(User)

    @property
    def data(self):
        return {
            'user_id': self.user_id,
            'user_name': self.user.name,
            'user_netid': self.user.netid,
            'assignment_id': self.assignment_id,
            'due_date': str(self.due_date)
        }
