import base64
import copy
import gzip
import os
from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import deferred, relationship, InstrumentedAttribute
from sqlalchemy.sql.schema import Column, ForeignKey

from anubis.constants import THEIA_DEFAULT_OPTIONS, DB_COLLATION, DB_CHARSET
from anubis.models.id import default_id_length, default_id
from anubis.models.sqltypes import String, Text, DateTime, Boolean, JSON, Integer
from anubis.utils.data import human_readable_timedelta

db = SQLAlchemy()


class Config(db.Model):
    __tablename__ = "anubis_config"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # Fields
    key: str = Column(String(length=128), primary_key=True)
    value: str = Column(String(length=2048))

    @property
    def data(self):
        return {
            "key":   self.key,
            "value": self.value,
        }


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # id
    id = default_id()

    # Fields
    netid: str = Column(String(length=128), unique=True, nullable=False)
    github_username = Column(Text(length=2 ** 14), index=True)
    name = Column(Text(length=2 ** 14))
    is_superuser: bool = Column(Boolean, nullable=False, default=False)
    is_anubis_developer: bool = Column(Boolean, nullable=False, default=False)
    disabled: bool = Column(Boolean, nullable=False, default=False)
    deadline_email_enabled: bool = Column(Boolean, nullable=False, default=True)
    release_email_enabled: bool = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    ta_for_course = relationship("TAForCourse", backref="owner")
    professor_for_course = relationship("ProfessorForCourse", backref="owner")
    in_course = relationship("InCourse", backref="owner")
    assignment_repos = relationship("AssignmentRepo", backref="owner")
    assigned_student_questions = relationship("AssignedStudentQuestion", backref="owner")
    submissions = relationship("Submission", backref="owner")
    theia_sessions = relationship("TheiaSession", backref="owner")
    late_exceptions = relationship("LateException", backref="user")
    forum_posts = relationship("ForumPost", backref="owner")
    forum_comments = relationship("ForumPostComment", backref="owner", foreign_keys="ForumPostComment.owner_id")
    forum_approved_comments = relationship(
        "ForumPostComment", backref="approved_by", foreign_keys="ForumPostComment.approved_by_id"
    )
    forum_upvotes = relationship("ForumPostUpvote", backref="owner")
    forum_posts_viewed = relationship("ForumPostViewed", backref="owner")

    @property
    def data(self):
        from anubis.lms.courses import get_user_permissions, get_beta_ui_enabled

        return {
            "id":                     self.id,
            "netid":                  self.netid,
            "github_username":        self.github_username,
            "name":                   self.name,
            "beta_ui_enabled":        get_beta_ui_enabled(self.netid),
            "deadline_email_enabled": self.deadline_email_enabled,
            "release_email_enabled":  self.release_email_enabled,
            "created":                str(self.created),
            **get_user_permissions(self),
        }

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<User {self.netid} {self.github_username}>"


class Course(db.Model):
    __tablename__ = "course"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # id
    id = default_id()

    # Fields
    name = Column(Text(length=2 ** 14), nullable=False)
    course_code = Column(Text(length=2 ** 14), nullable=False)
    semester = Column(Text(length=2 ** 14), nullable=True)
    section = Column(Text(length=2 ** 14), nullable=True)
    professor_display_name = Column(Text(length=2 ** 14))
    autograde_tests_repo = Column(
        Text(length=2 ** 14),
        nullable=False,
        default="https://github.com/os3224/anubis-assignment-tests",
    )
    github_repo_required: bool = Column(Boolean, default=True)
    theia_default_image_id: str = Column(String(length=default_id_length), ForeignKey("theia_image.id"), nullable=True)
    theia_default_options = Column(JSON, default=lambda: copy.deepcopy(THEIA_DEFAULT_OPTIONS))
    github_org: str = Column(String(length=256), default="os3224")
    github_ta_team_slug: str = Column(String(length=256), default="tas")
    join_code: str = Column(String(length=256), unique=True)
    display_visuals: bool = Column(Boolean, default=True)
    beta_ui_enabled: bool = Column(Boolean, default=False)

    assignments = relationship("Assignment", cascade="all,delete", backref="course")
    ta_for_course = relationship("TAForCourse", cascade="all,delete", backref="course")
    professor_for_course = relationship("ProfessorForCourse", cascade="all,delete", backref="course")
    in_course = relationship("InCourse", cascade="all,delete", backref="course")
    lecture_notes = relationship("LectureNotes", cascade="all,delete", backref="course")
    static_files = relationship("StaticFile", cascade="all,delete", backref="course")
    theia_sessions = relationship("TheiaSession", cascade="all,delete", backref="course")
    forum_posts = relationship("ForumPost", backref="course")
    forum_categories = relationship("ForumCategory", backref="course")

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
            "id":                     self.id,
            "name":                   self.name,
            "course_code":            self.course_code,
            "section":                self.section,
            "professor_display_name": self.professor_display_name,
            "total_assignments":      self.total_assignments,
            "open_assignment":        self.open_assignments,
            "join_code":              self.id[:6],
            "beta_ui_enabled":        self.beta_ui_enabled,
        }


class TAForCourse(db.Model):
    __tablename__ = "ta_for_course"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # Foreign Keys
    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id), primary_key=True)
    course_id: str = Column(String(length=default_id_length), ForeignKey(Course.id), primary_key=True)

    @property
    def data(self):
        return {
            "id":   self.course.id,
            "name": self.course.name,
        }


class ProfessorForCourse(db.Model):
    __tablename__ = "professor_for_course"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # Foreign Keys
    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id), primary_key=True)
    course_id: str = Column(String(length=default_id_length), ForeignKey(Course.id), primary_key=True)

    @property
    def data(self):
        return {
            "id":   self.course.id,
            "name": self.course.name,
        }


class InCourse(db.Model):
    __tablename__ = "in_course"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # Foreign Keys
    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id), primary_key=True)
    course_id: str = Column(String(length=default_id_length), ForeignKey(Course.id), primary_key=True)


class Assignment(db.Model):
    __tablename__ = "assignment"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # id
    id = default_id()

    # Foreign Keys
    course_id: str = Column(String(length=default_id_length), ForeignKey(Course.id), index=True)

    # Fields
    name = Column(Text(length=2 ** 14), nullable=False, index=True)
    hidden: bool = Column(Boolean, default=False)
    description = Column(Text(length=2 ** 14), nullable=True)
    unique_code = Column(
        String(length=8),
        unique=True,
        default=lambda: base64.b16encode(os.urandom(4)).decode().lower(),
    )
    accept_late: bool = Column(Boolean, default=True)
    hide_due_date: bool = Column(Boolean, default=False)
    questions_assigned: bool = Column(Boolean, default=False)
    email_notifications_enabled: bool = Column(Boolean, default=True, nullable=False)

    # Autograde
    pipeline_image = Column(Text(length=2 ** 14), nullable=True, index=True)
    autograde_enabled: bool = Column(Boolean, default=True)

    # IDE
    ide_enabled: bool = Column(Boolean, default=True)
    theia_image_id: str = Column(String(length=default_id_length), ForeignKey("theia_image.id"), default=None)
    theia_image_tag_id: str = Column(String(length=default_id_length), ForeignKey("theia_image_tag.id"), default=None)
    theia_options = Column(JSON, default=lambda: copy.deepcopy(THEIA_DEFAULT_OPTIONS))

    # Cheat Detection
    anti_cheat_enabled: bool = Column(Boolean, default=False)

    # Github
    github_template = Column(Text(length=2 ** 14), nullable=True, default="")
    github_repo_required: bool = Column(Boolean, default=False)

    # Dates
    release_date: datetime = Column(DateTime, nullable=False)
    due_date: datetime = Column(DateTime, nullable=False)
    grace_date: datetime = Column(DateTime, nullable=True)

    assignment_questions = relationship("AssignmentQuestion", cascade="all,delete", backref="assignment")
    assigned_student_questions = relationship("AssignedStudentQuestion", cascade="all,delete", backref="assignment")
    submissions = relationship("Submission", cascade="all,delete", backref="assignment")
    theia_sessions = relationship("TheiaSession", cascade="all,delete", backref="assignment")
    late_exceptions = relationship("LateException", cascade="all,delete", backref="assignment")
    tests = relationship("AssignmentTest", cascade="all,delete", backref="assignment")
    repos = relationship("AssignmentRepo", cascade="all,delete", backref="assignment")

    @property
    def data(self):
        return {
            "id":                   self.id,
            "name":                 self.name,
            "due_date":             str(self.due_date),
            "past_due":             self.due_date < datetime.now(),
            "hidden":               self.hidden,
            "accept_late":          self.accept_late,
            "autograde_enabled":    self.autograde_enabled,
            "hide_due_date":        self.hide_due_date,
            "course":               self.course.data,
            "description":          self.description,
            "visible_to_students":  not self.hidden and (datetime.now() > self.release_date),
            "ide_active":           self.due_date + timedelta(days=3 * 7) > datetime.now(),
            "tests":                [t.data for t in self.tests if t.hidden is False],
            # IDE
            "ide_enabled":          self.ide_enabled,
            "autosave":             self.theia_options.get("autosave", True),
            "persistent_storage":   self.theia_options.get("persistent_storage", False),
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
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # id
    id = default_id()

    # Foreign Keys
    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id), nullable=True)
    assignment_id: str = Column(String(length=default_id_length), ForeignKey(Assignment.id), nullable=False)

    # Fields
    netid: str = Column(String(length=128), nullable=False)
    repo_url: str = Column(String(length=512), nullable=False)
    shared: bool = Column(Boolean, default=False)

    # State booleans
    repo_created: bool = Column(Boolean, default=False)
    collaborator_configured: bool = Column(Boolean, default=False)
    ta_configured: bool = Column(Boolean, default=False)

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        return {
            "id":              self.id,
            "netid":           self.netid,
            "assignment_id":   self.assignment_id,
            "assignment_name": self.assignment.name,
            "shared":          self.shared,
            "ready":           self.repo_created,
            "course_code":     self.assignment.course.course_code,
            "repo_url":        self.repo_url,
        }


class AssignmentTest(db.Model):
    __tablename__ = "assignment_test"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # id
    id = default_id()

    # Foreign Keys
    assignment_id: str = Column(String(length=default_id_length), ForeignKey(Assignment.id))

    # Fields
    name = Column(Text(length=2 ** 14), index=True)
    hidden: bool = Column(Boolean, default=False)
    points: int = Column(Integer, default=10)

    @property
    def data(self):
        return {"id": self.id, "name": self.name, "hidden": self.hidden, "points": self.points}


class AssignmentQuestion(db.Model):
    __tablename__ = "assignment_question"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # id
    id = default_id()

    # Foreign Keys
    assignment_id: str = Column(String(length=default_id_length), ForeignKey(Assignment.id), index=True)

    # Fields
    question = Column(Text(length=2 ** 14), nullable=False)
    solution = Column(Text(length=2 ** 14), nullable=True)
    pool: int = Column(Integer, index=True, nullable=False)
    code_question: bool = Column(Boolean, default=False)
    code_language = Column(Text(length=2 ** 14), nullable=True, default="")
    placeholder = Column(Text(length=2 ** 14), nullable=True, default="")

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    shape = {"question": str, "solution": str, "pool": int}

    @property
    def full_data(self):
        return {
            "id":            self.id,
            "question":      self.question,
            "code_question": self.code_question,
            "code_language": self.code_language,
            "solution":      self.solution,
            "pool":          self.pool,
        }

    @property
    def data(self):
        return {
            "id":            self.id,
            "question":      self.question,
            "code_question": self.code_question,
            "code_language": self.code_language,
            "pool":          self.pool,
        }


class AssignedStudentQuestion(db.Model):
    __tablename__ = "assigned_student_question"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # id
    id = default_id()

    # Foreign Keys
    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id))
    assignment_id: str = Column(String(length=default_id_length), ForeignKey(Assignment.id), index=True, nullable=False)
    question_id: str = Column(
        String(length=default_id_length), ForeignKey(AssignmentQuestion.id), index=True, nullable=False
    )

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    question = relationship(AssignmentQuestion)
    responses = relationship("AssignedQuestionResponse", cascade="all,delete", backref="question")

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
            "late":      True,
            "text":      self.question.placeholder,
        }
        if response is not None:
            response_data = response.data

        return {
            "id":       self.id,
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
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # id
    id = default_id()

    # Foreign Keys
    assigned_question_id = Column(
        String(length=128),
        ForeignKey(AssignedStudentQuestion.id),
        index=True,
        nullable=False,
    )

    # Fields
    response = Column(Text(length=2 ** 14), default="", nullable=False)

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        from anubis.lms.assignments import get_assignment_due_date

        return {
            "submitted": str(self.created),
            "late":      get_assignment_due_date(self.question.owner.id, self.question.assignment.id) < self.created,
            "text":      self.response,
        }


class Submission(db.Model):
    __tablename__ = "submission"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # id
    id = default_id()

    # Foreign Keys
    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id), index=True, nullable=True)
    assignment_id: str = Column(String(length=default_id_length), ForeignKey(Assignment.id), index=True, nullable=False)
    assignment_repo_id: str = Column(String(length=default_id_length), ForeignKey(AssignmentRepo.id), nullable=False)

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Fields
    commit: str = Column(String(length=128), unique=True, index=True, nullable=False)
    processed: bool = Column(Boolean, default=False)
    state = Column(Text(length=2 ** 14), default="")
    errors = Column(JSON, default=None, nullable=True)
    token: str = Column(String(length=64), default=lambda: base64.b16encode(os.urandom(32)).decode())
    accepted: bool = Column(Boolean, default=True)

    # Relationships
    build = relationship(
        "SubmissionBuild",
        cascade="all,delete",
        uselist=False,
        backref="submission",
        lazy=False,
    )
    test_results = relationship("SubmissionTestResult", cascade="all,delete", backref="submission", lazy=False)
    repo = relationship(AssignmentRepo, backref="submissions")

    @property
    def data(self):
        return {
            "id":              self.id,
            "assignment_name": self.assignment.name,
            "assignment_due":  str(self.assignment.due_date),
            "course_code":     self.assignment.course.course_code,
            "commit":          self.commit,
            "processed":       self.processed,
            "state":           self.state,
            "created":         str(self.created),
            "last_updated":    str(self.last_updated),
            "error":           self.errors is not None,
        }

    @property
    def full_data(self):
        from anubis.lms.assignments import get_assignment_tests

        # Add connected models
        data = self.data
        data["repo"] = self.repo.repo_url
        data["tests"] = get_assignment_tests(self, only_visible=True)
        data["build"] = self.build.data if self.build is not None else None

        return data

    @property
    def admin_data(self):
        from anubis.lms.assignments import get_assignment_tests

        data = self.full_data
        data["tests"] = get_assignment_tests(self, only_visible=False)

        return data


class SubmissionTestResult(db.Model):
    __tablename__ = "submission_test_result"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # id
    id = default_id()

    # Foreign Keys
    submission_id: str = Column(String(length=default_id_length), ForeignKey(Submission.id), primary_key=True)
    assignment_test_id: str = Column(String(length=default_id_length), ForeignKey(AssignmentTest.id), primary_key=True)

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Fields
    output_type: str = Column(String(length=128), default="text")
    output = deferred(Column(Text(length=2 ** 16)))
    message = deferred(Column(Text(length=2 ** 10)))
    passed: bool = Column(Boolean)

    # Relationships
    assignment_test = relationship(AssignmentTest)

    @property
    def data(self):
        return {
            "id":           self.id,
            "test_name":    self.assignment_test.name,
            "passed":       self.passed,
            "message":      self.message,
            "output_type":  self.output_type,
            "output":       self.output,
            "created":      str(self.created),
            "last_updated": str(self.last_updated),
        }

    def __str__(self):
        return "testname: {}\nerrors: {}\npassed: {}\n".format(
            self.testname,
            self.errors,
            self.passed,
        )


class SubmissionBuild(db.Model):
    __tablename__ = "submission_build"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # id
    id = default_id()

    # Foreign Keys
    submission_id: str = Column(String(length=default_id_length), ForeignKey(Submission.id), index=True)

    # Fields
    stdout = deferred(Column(Text(length=2 ** 14)))
    passed: bool = Column(Boolean, default=None)

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        return {
            "stdout": self.stdout,
            "passed": self.passed,
        }


class TheiaImage(db.Model):
    __tablename__ = "theia_image"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    id = default_id()
    image: str = Column(String(length=1024), nullable=False, default="registry.digitalocean.com/anubis/xv6")
    title: str = Column(String(length=1024), default="")
    description = deferred(Column(Text(length=2 ** 14), default=""))
    icon: str = Column(String(length=1024), default="")
    public: bool = Column(Boolean, nullable=False, default=False)
    default_tag: str = Column(String(length=128), default="latest")
    icon: str = Column(String(length=128))
    webtop: bool = Column(Boolean, default=False)

    courses = relationship(Course, backref="theia_default_image")
    assignments = relationship(Assignment, backref="theia_image")
    sessions = relationship("TheiaSession", backref="image")
    tags = relationship("TheiaImageTag", backref="image")

    @property
    def data(self):
        return {
            "id":          self.id,
            "image":       self.image,
            "title":       self.title,
            "description": self.description,
            "icon":        self.icon,
            "public":      self.public,
            "default_tag": self.default_tag,
            "webtop":      self.webtop,
            "tags":        list(sorted(
                [tag.data for tag in self.tags],
                key=lambda tag_data: tag_data['title']
            )),
        }


class TheiaImageTag(db.Model):
    __tablename__ = "theia_image_tag"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    id = default_id()
    image_id: str = Column(String(length=default_id_length), ForeignKey(TheiaImage.id), nullable=False)
    tag: str = Column(String(length=256), nullable=False, default="latest")
    title: str = Column(String(length=1024), nullable=False, default="")
    description: str = Column(String(length=1024), nullable=False, default="")

    assignments = relationship(Assignment, backref="image_tag")
    sessions = relationship("TheiaSession", backref="image_tag")

    @property
    def data(self):
        return {
            "id":          self.id,
            "image_id":    self.image_id,
            "tag":         self.tag,
            "title":       self.title,
            "description": self.description,
        }


class TheiaSession(db.Model):
    __tablename__ = "theia_session"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    # id
    id = default_id()

    # Foreign keys
    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id), nullable=False)
    course_id: str = Column(String(length=default_id_length), ForeignKey(Course.id), nullable=True, index=True)
    assignment_id: str = Column(String(length=default_id_length), ForeignKey(Assignment.id), nullable=True)
    image_id: str = Column(String(length=default_id_length), ForeignKey(TheiaImage.id), nullable=True)
    image_tag_id: str = Column(String(length=default_id_length), ForeignKey(TheiaImageTag.id), nullable=True)

    # Fields
    playground: bool = Column(Boolean, default=False)
    repo_url: str = Column(String(length=128), nullable=True)
    active: bool = Column(Boolean, default=True)
    state = Column(Text(length=2 ** 14))
    cluster_address = Column(Text(length=2 ** 14), nullable=True, default=None)

    # IDE settings
    resources = Column(JSON, default=lambda: {})
    network_policy: str = Column(String(length=128), default="os-student")
    network_locked: bool = Column(Boolean, default=True)
    autosave: bool = Column(Boolean, default=True)
    credentials: bool = Column(Boolean, default=False)
    persistent_storage: bool = Column(Boolean, default=False)
    admin: bool = Column(Boolean, default=False)
    docker: bool = Column(Boolean, default=False)

    k8s_requested: bool = Column(Boolean, default=False)

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    ended: datetime = Column(DateTime, nullable=True, default=None)
    last_proxy: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        from anubis.ide.redirect import theia_redirect_url

        return {
            "id":                 self.id,
            "assignment_id":      self.assignment_id,
            "assignment_name":    self.assignment.name if self.assignment_id is not None else None,
            "course_code":        self.assignment.course.course_code if self.assignment_id is not None else None,
            "playground":         self.playground,
            "netid":              self.owner.netid,
            "name":               self.owner.name,
            "repo_url":           self.repo_url,
            "redirect_url":       theia_redirect_url(self.id, self.owner.netid),
            "active":             self.active,
            "state":              self.state,
            "created":            str(self.created),
            "created_delta":      human_readable_timedelta(datetime.now() - self.created),
            "ended":              str(self.ended),
            "last_proxy":         str(self.last_proxy),
            "last_proxy_delta":   human_readable_timedelta(datetime.now() - self.last_proxy),
            "last_updated":       str(self.last_updated),
            "autosave":           self.autosave,
            "persistent_storage": self.persistent_storage,
            "image":              self.image.data if self.image_id else None,
            "image_tag":          self.image_tag.data if self.image_tag_id else None,
        }

    @property
    def settings(self):
        return {
            "admin":              self.admin,
            "image":              self.image.data,
            "repo_url":           self.repo_url,
            "autosave":           self.autosave,
            "credentials":        self.credentials,
            "network_locked":     self.network_locked,
            "persistent_storage": self.persistent_storage,
        }


class TheiaPaste(db.Model):
    __tablename__ = "theia_paste"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    id = default_id()

    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id), index=True)
    theia_session_id: str = Column(String(length=default_id_length), ForeignKey(TheiaSession.id), index=True)
    timestamp: datetime = Column(DateTime, default=datetime.now)

    content = deferred(Column(db.LargeBinary(2 ** 12)))

    @property
    def data(self):
        return {
            "id":               self.id,
            "owner_id":         self.owner_id,
            "theia_session_id": self.theia_session_id,
            "timestamp":        self.timestamp,
            "content":          self.content,
        }


class StaticFile(db.Model):
    __tablename__ = "static_file"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    id = default_id()
    course_id: str = Column(String(length=default_id_length), ForeignKey(Course.id), nullable=False, index=True)

    # Fields
    filename = Column(Text(length=2 ** 14))
    path = Column(Text(length=2 ** 14))
    content_type = Column(Text(length=2 ** 14))
    _blob = deferred(Column(db.LargeBinary(length=(2 ** 32) - 1)))
    hidden: bool = Column(Boolean, default=False)

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    lecture_notes = relationship("LectureNotes", cascade="all,delete", backref="static_file")

    @hybrid_property
    def blob(self):
        if isinstance(self._blob, InstrumentedAttribute):
            return self._blob
        return gzip.decompress(self._blob)

    @blob.setter
    def blob(self, blob):
        if isinstance(blob, str):
            self._blob = gzip.compress(blob.encode())
        elif isinstance(blob, bytes):
            self._blob = gzip.compress(blob)
        else:
            self._blob = gzip.compress(b"")

    @property
    def data(self):
        return {
            "id":           self.id,
            "content_type": self.content_type,
            "filename":     self.filename,
            "path":         self.path,
            "hidden":       self.hidden,
            "uploaded":     str(self.created),
        }


class LateException(db.Model):
    __tablename__ = "late_exception"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id), primary_key=True)
    assignment_id: str = Column(String(length=default_id_length), ForeignKey(Assignment.id), primary_key=True)

    # New Due Date
    due_date: datetime = Column(DateTime, nullable=False)

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        return {
            "owner_id":      self.owner_id,
            "user_name":     self.user.name,
            "user_netid":    self.user.netid,
            "assignment_id": self.assignment_id,
            "due_date":      str(self.due_date),
        }


class LectureNotes(db.Model):
    __tablename__ = "lecture_notes"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    id = default_id()

    # Foreign keys
    static_file_id: str = Column(
        String(length=default_id_length), ForeignKey(StaticFile.id), nullable=False, index=True
    )
    course_id: str = Column(String(length=default_id_length), ForeignKey(Course.id), nullable=False, index=True)

    # Meta fields
    post_time: datetime = Column(DateTime, nullable=True, default=datetime.now)
    title = Column(Text(length=2 ** 14), default="")
    description = Column(Text(length=2 ** 14), default="")
    hidden: bool = Column(Boolean, default=False)

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        return {
            "id":           self.id,
            "static_file":  self.static_file.data,
            "course":       self.course.course_code,
            "title":        self.title,
            "description":  self.description,
            "hidden":       self.hidden,
            "post_time":    str(self.post_time),
            "created":      str(self.created),
            "last_updated": str(self.last_updated),
        }


class ForumPost(db.Model):
    __tablename__ = "forum_post"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    id = default_id()

    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id), nullable=False)
    course_id: str = Column(String(length=default_id_length), ForeignKey(Course.id))
    visible_to_students: bool = Column(Boolean, default=False)
    pinned: bool = Column(Boolean, default=False)
    anonymous: bool = Column(Boolean, default=False)
    seen_count: int = Column(Integer, default=0)

    # Content
    title = Column(Text(length=1024))
    content = deferred(Column(Text(length=2 ** 14)))

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    comments = relationship("ForumPostComment", cascade="all,delete", backref="post")
    in_categories = relationship("ForumPostInCategory", cascade="all,delete", backref="post")
    views = relationship("ForumPostViewed", cascade="all,delete", backref="post")
    upvotes = relationship("ForumPostUpvote", cascade="all,delete", backref="post")

    @property
    def meta_data(self):
        return {
            "id":                  self.id,
            "title":               self.title,
            "anonymous":           self.anonymous,
            "display_name":        "Anonymous" if self.anonymous else self.owner.name,
            "course_id":           self.course_id,
            "visible_to_students": self.visible_to_students,
            "pinned":              self.pinned,
            "seen_count":          self.seen_count,
            "created":             str(self.created),
            "last_updated":        str(self.last_updated),
        }

    @property
    def data(self):
        from anubis.lms.forum import get_post_comments_data

        data = self.meta_data
        data["title"] = self.title
        data["content"] = self.content
        data["comments"] = get_post_comments_data(self)
        return data

    @property
    def admin_data(self):
        data = self.data
        data["display_name"] = self.owner.name
        return data


class ForumCategory(db.Model):
    __tablename__ = "forum_category"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    id = default_id()

    name: str = Column(String(length=128))
    course_id: str = Column(String(length=default_id_length), ForeignKey(Course.id))

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    in_category = relationship("ForumPostInCategory", cascade="all,delete", backref="category")

    @property
    def data(self):
        return {
            "id":           self.id,
            "name":         self.name,
            "course_id":    self.course_id,
            "created":      str(self.created),
            "last_updated": str(self.last_updated),
        }


class ForumPostInCategory(db.Model):
    __tablename__ = "forum_post_in_category"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    post_id: str = Column(String(length=default_id_length), ForeignKey(ForumPost.id), primary_key=True)
    category_id: str = Column(String(length=default_id_length), ForeignKey(ForumCategory.id), primary_key=True)

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        return {
            "post_id":      self.post_id,
            "category_id":  self.category_id,
            "created":      str(self.created),
            "last_updated": str(self.last_updated),
        }


class ForumPostViewed(db.Model):
    __tablename__ = "forum_post_viewed"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id), primary_key=True)
    post_id: str = Column(String(length=default_id_length), ForeignKey(ForumPost.id), primary_key=True)

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        return {
            "owner_id":     self.owner_id,
            "post_id":      self.post_id,
            "created":      str(self.created),
            "last_updated": str(self.last_updated),
        }


class ForumPostComment(db.Model):
    __tablename__ = "forum_post_comment"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    id = default_id()

    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id), nullable=False)
    post_id: str = Column(String(length=default_id_length), ForeignKey(ForumPost.id), nullable=False)
    parent_id: str = Column(String(length=default_id_length), nullable=True)
    approved_by_id: str = Column(String(length=default_id_length), ForeignKey(User.id), nullable=True)
    anonymous: bool = Column(Boolean, default=False)
    thread_start: bool = Column(Boolean, default=False)

    content: str = deferred(Column(Text(length=2 ** 12)))

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def meta_data(self):
        return {
            "id":           self.id,
            "anonymous":    self.anonymous,
            "display_name": "Anonymous" if self.anonymous else self.owner.name,
            "post_id":      self.post_id,
            "parent_id":    self.parent_id,
            "approved_by":  self.approved_by.name if self.approved_by_id is not None else None,
            "thread_start": self.thread_start,
            "created":      str(self.created),
            "last_updated": str(self.last_updated),
        }

    @property
    def data(self):
        data = self.meta_data
        data["content"] = self.content
        return data

    @property
    def admin_data(self):
        data = self.data
        data["display_name"] = self.owner.name
        return data


class ForumPostUpvote(db.Model):
    __tablename__ = "forum_post_upvote"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    id = default_id()

    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id), primary_key=True)
    post_id: str = Column(String(length=default_id_length), ForeignKey(ForumPost.id), primary_key=True)

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        return {
            "owner_id":     self.owner_id,
            "post_id":      self.post_id,
            "created":      str(self.created),
            "last_updated": str(self.last_updated),
        }


class EmailTemplate(db.Model):
    __tablename__ = "email_template"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    key: str = Column(String(length=128), primary_key=True, index=True)
    body: str = Column(String(length=4096))
    subject: str = Column(String(length=1024))

    @property
    def data(self):
        return {
            "key":     self.key,
            "body":    self.body,
            "subject": self.subject,
        }


class EmailEvent(db.Model):
    __tablename__ = "email_event"
    __table_args__ = {"mysql_charset": DB_CHARSET, "mysql_collate": DB_COLLATION}

    id: str = default_id()

    # Who the email was sent to
    owner_id: str = Column(String(length=default_id_length), ForeignKey(User.id))

    # Email Template used
    template_id: str = Column(String(length=128), ForeignKey(EmailTemplate.key))

    # The id of the thing that was referenced (like say an assignment id for
    # a deadline notification)
    reference_id: str = Column(String(length=default_id_length))

    # The type of thing being referenced in reference id (like "assignment_deadline" if
    # it is an assignment deadline)
    reference_type: str = Column(String(length=128))

    # Email subject and body
    subject: str = deferred(Column(String(2048)))
    body: str = deferred(Column(String(8192)))

    # Timestamps
    created: datetime = Column(DateTime, default=datetime.now)
    last_updated: datetime = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def data(self):
        return {
            "owner_id":       self.owner_id,
            "template_id":    self.template_id,
            "reference_id":   self.reference_id,
            "reference_type": self.reference_type,
            "subject":        self.subject,
            "body":           self.body,
            "created":        str(self.created),
            "last_updated":   str(self.last_updated),
        }
