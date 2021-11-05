import base64
import copy
import os
from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import deferred
from sqlalchemy_json import MutableJson

from anubis.utils.data import rand

db = SQLAlchemy()

THEIA_DEFAULT_OPTIONS = {
    "autosave": True,
    "persistent_storage": False,
    "network_policy": "os-student",
    "resources": {
        "requests": {"cpu": "300m", "memory": "300Mi"},
        "limits": {"cpu": "2", "memory": "500Mi"},
    },
}


def default_id(max_len=None) -> db.Column:
    return db.Column(db.String(128), primary_key=True, default=lambda: rand(max_len or 32))


class Config(db.Model):
    __tablename__ = "anubis_config"

    # Fields
    key = db.Column(db.String(128), primary_key=True)
    value = db.Column(db.String(2048))

    @property
    def data(self):
        return {
            "key": self.key,
            "value": self.value,
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

    ta_for_course = db.relationship("TAForCourse", cascade="all,delete", backref="owner")
    professor_for_course = db.relationship("ProfessorForCourse", cascade="all,delete", backref="owner")
    in_course = db.relationship("InCourse", cascade="all,delete", backref="owner")
    assignment_repos = db.relationship("AssignmentRepo", cascade="all,delete", backref="owner")
    assigned_student_questions = db.relationship("AssignedStudentQuestion", cascade="all,delete", backref="owner")
    submissions = db.relationship("Submission", cascade="all,delete", backref="owner")
    theia_sessions = db.relationship("TheiaSession", cascade="all,delete", backref="owner")
    late_exceptions = db.relationship("LateException", cascade="all,delete", backref="user")

    @property
    def data(self):
        from anubis.lms.courses import get_user_permissions

        return {
            "id": self.id,
            "netid": self.netid,
            "github_username": self.github_username,
            "name": self.name,
            **get_user_permissions(self),
        }

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<User {self.netid} {self.github_username}>"


class Course(db.Model):
    __tablename__ = "course"

    # id
    id = default_id()

    # Fields
    name = db.Column(db.TEXT, nullable=False)
    course_code = db.Column(db.TEXT, nullable=False)
    semester = db.Column(db.TEXT, nullable=True)
    section = db.Column(db.TEXT, nullable=True)
    professor_display_name = db.Column(db.TEXT)
    autograde_tests_repo = db.Column(
        db.TEXT,
        nullable=False,
        default="https://github.com/os3224/anubis-assignment-tests",
    )
    github_repo_required = db.Column(db.Boolean, default=True)
    theia_default_image = db.Column(db.TEXT, nullable=False, default="registry.digitalocean.com/anubis/theia-xv6")
    theia_default_options = db.Column(MutableJson, default=lambda: copy.deepcopy(THEIA_DEFAULT_OPTIONS))
    github_org = db.Column(db.TEXT, default="os3224")
    join_code = db.Column(db.String(256), unique=True)
    display_visuals = db.Column(db.Boolean, default=True)

    assignments = db.relationship("Assignment", cascade="all,delete", backref="course")
    ta_for_course = db.relationship("TAForCourse", cascade="all,delete", backref="course")
    professor_for_course = db.relationship("ProfessorForCourse", cascade="all,delete", backref="course")
    in_course = db.relationship("InCourse", cascade="all,delete", backref="course")
    lecture_notes = db.relationship("LectureNotes", cascade="all,delete", backref="course")
    static_files = db.relationship("StaticFile", cascade="all,delete", backref="course")
    theia_sessions = db.relationship("TheiaSession", cascade="all,delete", backref="course")

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
            "professor_display_name": self.professor_display_name,
            "total_assignments": self.total_assignments,
            "open_assignment": self.open_assignments,
            "join_code": self.id[:6],
        }


class TAForCourse(db.Model):
    __tablename__ = "ta_for_course"

    # Foreign Keys
    owner_id = db.Column(db.String(128), db.ForeignKey(User.id), primary_key=True)
    course_id = db.Column(db.String(128), db.ForeignKey(Course.id), primary_key=True)

    @property
    def data(self):
        return {
            "id": self.course.id,
            "name": self.course.name,
        }


class ProfessorForCourse(db.Model):
    __tablename__ = "professor_for_course"

    # Foreign Keys
    owner_id = db.Column(db.String(128), db.ForeignKey(User.id), primary_key=True)
    course_id = db.Column(db.String(128), db.ForeignKey(Course.id), primary_key=True)

    @property
    def data(self):
        return {
            "id": self.course.id,
            "name": self.course.name,
        }


class InCourse(db.Model):
    __tablename__ = "in_course"

    # Foreign Keys
    owner_id = db.Column(db.String(128), db.ForeignKey(User.id), primary_key=True)
    course_id = db.Column(db.String(128), db.ForeignKey(Course.id), primary_key=True)


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
    unique_code = db.Column(
        db.String(8),
        unique=True,
        default=lambda: base64.b16encode(os.urandom(4)).decode().lower(),
    )
    accept_late = db.Column(db.Boolean, default=True)
    hide_due_date = db.Column(db.Boolean, default=False)
    questions_assigned = db.Column(db.Boolean, default=False)

    # Autograde
    pipeline_image = db.Column(db.TEXT, nullable=True, index=True)
    autograde_enabled = db.Column(db.Boolean, default=True)

    # IDE
    ide_enabled = db.Column(db.Boolean, default=True)
    theia_image = db.Column(db.TEXT, default="registry.digitalocean.com/anubis/theia-xv6")
    theia_options = db.Column(MutableJson, default=lambda: copy.deepcopy(THEIA_DEFAULT_OPTIONS))

    # Github
    github_template = db.Column(db.TEXT, nullable=True, default="")
    github_repo_required = db.Column(db.Boolean, default=False)

    # Dates
    release_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    grace_date = db.Column(db.DateTime, nullable=True)

    assignment_questions = db.relationship("AssignmentQuestion", cascade="all,delete", backref="assignment")
    assigned_student_questions = db.relationship("AssignedStudentQuestion", cascade="all,delete", backref="assignment")
    submissions = db.relationship("Submission", cascade="all,delete", backref="assignment")
    theia_sessions = db.relationship("TheiaSession", cascade="all,delete", backref="assignment")
    late_exceptions = db.relationship("LateException", cascade="all,delete", backref="assignment")
    tests = db.relationship("AssignmentTest", cascade="all,delete", backref="assignment")
    repos = db.relationship("AssignmentRepo", cascade="all,delete", backref="assignment")

    @property
    def data(self):
        return {
            "id": self.id,
            "name": self.name,
            "due_date": str(self.due_date),
            "past_due": self.due_date < datetime.now(),
            "hidden": self.hidden,
            "accept_late": self.accept_late,
            "autograde_enabled": self.autograde_enabled,
            "hide_due_date": self.hide_due_date,
            "course": self.course.data,
            "description": self.description,
            "visible_to_students": not self.hidden and (datetime.now() > self.release_date),
            "ide_active": self.due_date + timedelta(days=3 * 7) > datetime.now(),
            "tests": [t.data for t in self.tests if t.hidden is False],
            # IDE
            "ide_enabled": self.ide_enabled,
            "autosave": self.theia_options.get("autosave", True),
            "persistent_storage": self.theia_options.get("persistent_storage", False),
            # Github
            "github_repo_required": self.github_repo_required,
        }

    @property
    def full_data(self):
        data = self.data
        data["tests"] = [t.data for t in self.tests]
        return data


class AssignmentRepo(db.Model):
    __tablename__ = "assignment_repo"

    # id
    id = default_id()

    # Foreign Keys
    owner_id = db.Column(db.String(128), db.ForeignKey(User.id), nullable=True)
    assignment_id = db.Column(db.String(128), db.ForeignKey(Assignment.id), nullable=False)

    # Fields
    github_username = db.Column(db.TEXT, nullable=False)
    repo_url = db.Column(db.String(512), nullable=False)

    # State booleans
    repo_created = db.Column(db.Boolean, default=False)
    collaborator_configured = db.Column(db.Boolean, default=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        return {
            "id": self.id,
            "github_username": self.github_username,
            "assignment_id": self.assignment_id,
            "assignment_name": self.assignment.name,
            "ready": self.repo_created and self.collaborator_configured,
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
        return {"id": self.id, "name": self.name, "hidden": self.hidden}


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
    code_language = db.Column(db.TEXT, nullable=True, default="")
    placeholder = db.Column(db.Text, nullable=True, default="")

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

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
    assignment_id = db.Column(db.String(128), db.ForeignKey(Assignment.id), index=True, nullable=False)
    question_id = db.Column(db.String(128), db.ForeignKey(AssignmentQuestion.id), index=True, nullable=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    question = db.relationship(AssignmentQuestion)
    responses = db.relationship("AssignedQuestionResponse", cascade="all,delete", backref="question")

    @property
    def data(self):
        """
        Returns simple dictionary representation of the object.

        :return:
        """

        response: AssignedQuestionResponse = (
            AssignedQuestionResponse.query.filter(
                AssignedQuestionResponse.assigned_question_id == self.id,
            )
            .order_by(AssignedQuestionResponse.created.desc())
            .first()
        )

        response_data = {
            "submitted": None,
            "late": True,
            "text": self.question.placeholder,
        }
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
        data["question"] = self.question.full_data
        return data


class AssignedQuestionResponse(db.Model):
    __tablename__ = "assigned_student_response"

    # id
    id = default_id()

    # Foreign Keys
    assigned_question_id = db.Column(
        db.String(128),
        db.ForeignKey(AssignedStudentQuestion.id),
        index=True,
        nullable=False,
    )

    # Fields
    response = db.Column(db.TEXT, default="", nullable=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        from anubis.lms.assignments import get_assignment_due_date

        return {
            "submitted": str(self.created),
            "late": get_assignment_due_date(self.question.owner.id, self.question.assignment.id) < self.created,
            "text": self.response,
        }


class Submission(db.Model):
    __tablename__ = "submission"

    # id
    id = default_id()

    # Foreign Keys
    owner_id = db.Column(db.String(128), db.ForeignKey(User.id), index=True, nullable=True)
    assignment_id = db.Column(db.String(128), db.ForeignKey(Assignment.id), index=True, nullable=False)
    assignment_repo_id = db.Column(db.String(128), db.ForeignKey(AssignmentRepo.id), nullable=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Fields
    commit = db.Column(db.String(128), unique=True, index=True, nullable=False)
    processed = db.Column(db.Boolean, default=False)
    state = db.Column(db.TEXT, default="")
    errors = db.Column(MutableJson, default=None, nullable=True)
    token = db.Column(db.String(64), default=lambda: base64.b16encode(os.urandom(32)).decode())
    accepted = db.Column(db.Boolean, default=True)

    # Relationships
    build = db.relationship(
        "SubmissionBuild",
        cascade="all,delete",
        uselist=False,
        backref="submission",
        lazy=False,
    )
    test_results = db.relationship("SubmissionTestResult", cascade="all,delete", backref="submission", lazy=False)
    repo = db.relationship(AssignmentRepo, backref="submissions")

    @property
    def visible_tests(self):
        """
        Get a list of dictionaries of the matching Test, and TestResult
        for the current submission.

        :return:
        """

        # Query for matching AssignmentTests, and TestResults
        tests = (
            SubmissionTestResult.query.join(AssignmentTest)
            .filter(
                SubmissionTestResult.submission_id == self.id,
                AssignmentTest.hidden == False,
            )
            .all()
        )

        # Convert to dictionary data
        return [{"test": result.assignment_test.data, "result": result.data} for result in tests]

    @property
    def all_tests(self):
        """
        Get a list of dictionaries of the matching Test, and TestResult
        for the current submission.

        :return:
        """

        # Query for matching AssignmentTests, and TestResults
        tests = (
            SubmissionTestResult.query.join(AssignmentTest)
            .filter(
                SubmissionTestResult.submission_id == self.id,
            )
            .all()
        )

        # Convert to dictionary data
        return [{"test": result.assignment_test.data, "result": result.data} for result in tests]

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
    submission_id = db.Column(db.String(128), db.ForeignKey(Submission.id), primary_key=True)
    assignment_test_id = db.Column(db.String(128), db.ForeignKey(AssignmentTest.id), primary_key=True)

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
    assignment_id = db.Column(db.String(128), db.ForeignKey(Assignment.id), nullable=True)
    repo_url = db.Column(db.String(128), nullable=True)

    # Fields
    active = db.Column(db.Boolean, default=True)
    state = db.Column(db.TEXT)
    cluster_address = db.Column(db.TEXT, nullable=True, default=None)
    image = db.Column(db.TEXT, default="registry.digitalocean.com/anubis/theia-xv6")

    resources = db.Column(MutableJson, default=lambda: {})
    network_policy = db.Column(db.String(128), default="os-student")
    network_locked = db.Column(db.Boolean, default=True)
    privileged = db.Column(db.Boolean, default=False)
    autosave = db.Column(db.Boolean, default=True)
    credentials = db.Column(db.Boolean, default=False)
    persistent_storage = db.Column(db.Boolean, default=False)
    k8s_requested = db.Column(db.Boolean, default=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    ended = db.Column(db.DateTime, nullable=True, default=None)
    last_proxy = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        from anubis.lms.theia import theia_redirect_url

        return {
            "id": self.id,
            "assignment_id": self.assignment_id,
            "assignment_name": self.assignment.name if self.assignment_id is not None else None,
            "course_code": self.assignment.course.course_code if self.assignment_id is not None else None,
            "netid": self.owner.netid,
            "repo_url": self.repo_url,
            "redirect_url": theia_redirect_url(self.id, self.owner.netid),
            "active": self.active,
            "state": self.state,
            "created": str(self.created),
            "ended": str(self.ended),
            "last_proxy": str(self.last_proxy),
            "last_updated": str(self.last_updated),
            "autosave": self.autosave,
            "persistent_storage": self.persistent_storage,
        }

    @property
    def settings(self):
        return {
            "image": self.image,
            "repo_url": self.repo_url,
            "autosave": self.autosave,
            "privileged": self.privileged,
            "credentials": self.credentials,
            "network_locked": self.network_locked,
            "persistent_storage": self.persistent_storage,
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
    hidden = db.Column(db.Boolean, default=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    lecture_notes = db.relationship("LectureNotes", cascade="all,delete", backref="static_file")

    @property
    def data(self):
        return {
            "id": self.id,
            "content_type": self.content_type,
            "filename": self.filename,
            "path": self.path,
            "hidden": self.hidden,
            "uploaded": str(self.created),
        }


class LateException(db.Model):
    __tablename__ = "late_exception"

    user_id = db.Column(db.String(128), db.ForeignKey(User.id), primary_key=True)
    assignment_id = db.Column(db.String(128), db.ForeignKey(Assignment.id), primary_key=True)

    # New Due Date
    due_date = db.Column(db.DateTime, nullable=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user.name,
            "user_netid": self.user.netid,
            "assignment_id": self.assignment_id,
            "due_date": str(self.due_date),
        }


class LectureNotes(db.Model):
    __tablename__ = "lecture_notes"

    id = default_id()

    # Foreign keys
    static_file_id = db.Column(db.String(128), db.ForeignKey(StaticFile.id), nullable=False, index=True)
    course_id = db.Column(db.String(128), db.ForeignKey(Course.id), nullable=False, index=True)

    # Meta fields
    post_time = db.Column(db.DateTime, nullable=True, default=datetime.now)
    title = db.Column(db.TEXT, default="")
    description = db.Column(db.TEXT, default="")
    hidden = db.Column(db.Boolean, default=False)

    # Timestamps
    created = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        return {
            "id": self.id,
            "static_file": self.static_file.data,
            "course": self.course.course_code,
            "title": self.title,
            "description": self.description,
            "hidden": self.hidden,
            "post_time": str(self.post_time),
            "created": str(self.created),
            "last_updated": str(self.last_updated),
        }
