import base64
import copy
import json
import os
import sys
import traceback
from typing import Any, Callable, List

import requests

from anubis.app import create_app
from anubis.models import AssignmentRepo, Course, InCourse, ProfessorForCourse, TAForCourse, User, db
from anubis.utils.data import with_context
from anubis.utils.testing.seed import create_name, create_netid

os.environ["DEBUG"] = "1"
os.environ["DISABLE_ELK"] = "1"
os.environ["DB_HOST"] = "127.0.0.1"
os.environ["CACHE_REDIS_HOST"] = "127.0.0.1"


def initialize_env():
    os.environ["DB_HOST"] = "127.0.0.1"
    os.environ["REDIS_HOST"] = "127.0.0.1"
    os.environ["DISABLE_ELK"] = "1"
    os.environ["DEBUG"] = "1"

    test_root = os.path.dirname(__file__)
    api_root = os.path.dirname(test_root)

    if test_root not in sys.path:
        sys.path.append(test_root)

    if api_root not in sys.path:
        sys.path.append(api_root)


def format_exception(e: Exception):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)

    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str


def print_full_error(e, r):
    print("Printing only the traceback above the current stack frame")
    print("".join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])))
    print()
    print("Printing the full traceback as if we had not caught it here...")
    print()
    format_exception(e)
    print(r.text)
    print(f"status_code={r.status_code}")
    print(r.url)
    exit(1)


@with_context
def create_user(permission: str = "superuser", add_to_os: bool = True):
    assert permission in ["superuser", "professor", "ta", "student"]

    name = create_name()
    netid = create_netid(name)

    # Create user in db
    user = User(
        netid=netid,
        name=name,
        github_username=netid,
        is_superuser=permission == "superuser",
    )
    db.session.add(user)

    course = Course.query.filter(Course.name == "Intro to OS").first()

    if add_to_os:
        db.session.add(
            InCourse(
                owner=user,
                course=course,
            )
        )
    if permission == "ta":
        db.session.add(
            TAForCourse(
                course=course,
                owner=user,
            )
        )
    if permission == "professor":
        db.session.add(
            ProfessorForCourse(
                course=course,
                owner=user,
            )
        )
    db.session.commit()

    return netid


def _create_user_session(url: str, netid: str = "superuser", new: bool = False, add_to_os: bool = True):
    """
    Create a new user on the backend

    :return: requests session
    """

    # Create requests session
    session = requests.session()

    if new:
        netid = create_user(netid, add_to_os)

    session.get(url + f"/admin/auth/token/{netid}")
    r = session.get(url + "/public/auth/whoami")

    try:
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["data"] is not None
        assert data["error"] is None
        data = copy.deepcopy(data)
        admin_for = data["data"]["user"]["admin_for"]
        for i in admin_for:
            if i["name"] == "Intro to OS":
                session.cookies["course"] = base64.urlsafe_b64encode(json.dumps(i).encode()).decode()
    except AssertionError as e:
        print_full_error(e, r)
    return session, netid


class Session(object):
    """
    This object will provide you with a functioning test session with
    a ransom user set up with it. You can call the get and post functions
    to move data between the session and the api.

    test_session = TestSession()
    data = test_session.get('/api/auth/whoami')
    # data ->> {'email': 'test.abcyf.1@pc.email', ...}
    """

    def __init__(
        self,
        permission: str = "superuser",
        new: bool = False,
        add_to_os: bool = True,
        domain: str = "localhost",
        port: int = 5000,
    ):
        self.url = f"http://{domain}:{port}"
        self.timings: List[Any] = []
        self._session, self.netid = _create_user_session(self.url, permission, new=new, add_to_os=add_to_os)

    @staticmethod
    def _verify_success(r):
        try:
            assert r.status_code == 200
            data = r.json()
            assert data["success"] is True
            assert data["data"] is not None
            assert data["error"] is None
        except AssertionError as e:
            print_full_error(e, r)

    @staticmethod
    def _verify_error(r):
        try:
            data = r.json()
            assert data["success"] is False
            assert data["data"] is None
            assert data["error"] is not None
        except AssertionError as e:
            print_full_error(e, r)

    def _verify(self, r, should_succeed, should_fail, skip_verify):
        response = None
        if not skip_verify:
            # Verify response succeeded
            if should_fail:
                self._verify_error(r)
                response = r.json()["error"]

            # Verify response failed
            if not should_fail and should_succeed:
                self._verify_success(r)
                response = r.json()["data"]
        return response

    def _make_request(
        self,
        path,
        request_func,
        return_request,
        should_succeed,
        should_fail,
        skip_verify,
        **kwargs,
    ):
        # Make the request
        r = request_func(self.url + path, **kwargs)

        # Add to timings
        self.timings.append(r.elapsed.microseconds)

        # Verify success or failure
        response = self._verify(r, should_succeed, should_fail, skip_verify)

        if return_request or response is None:
            return r

        # return filtered data
        return response

    def get(
        self,
        path,
        return_request=False,
        should_succeed=True,
        should_fail=False,
        skip_verify=False,
        **kwargs,
    ):
        return self._make_request(
            path,
            self._session.get,
            return_request,
            should_succeed,
            should_fail,
            skip_verify,
            **kwargs,
        )

    def post(
        self,
        path,
        return_request=False,
        should_succeed=True,
        should_fail=False,
        skip_verify=False,
        **kwargs,
    ):
        return self._make_request(
            path,
            self._session.post,
            return_request,
            should_succeed,
            should_fail,
            skip_verify,
            **kwargs,
        )

    def post_json(
        self,
        path,
        json,
        return_request=False,
        should_succeed=True,
        should_fail=False,
        skip_verify=False,
        **kwargs,
    ):
        kwargs["json"] = json
        if "headers" not in kwargs:
            kwargs["headers"] = dict()
        kwargs["headers"]["Content-Type"] = "application/json"

        return self._make_request(
            path,
            self._session.post,
            return_request,
            should_succeed,
            should_fail,
            skip_verify,
            **kwargs,
        )


def pp(data: dict):
    print(json.dumps(data, indent=2))


def run_main(func):
    app = create_app()
    with app.app_context():
        return func()


@with_context
def create_repo(s: Session, assignment_id: str = None):
    from anubis.lms.repos import get_repos
    from anubis.utils.cache import cache

    if assignment_id is None:
        assignments = s.get("/public/assignments/list")["assignments"]
        assignment_id = assignments[0]["id"]
    user = User.query.filter(User.netid == s.netid).first()
    db.session.add(
        AssignmentRepo(
            owner=user,
            assignment_id=assignment_id,
            github_username=s.netid,
            repo_url="https://github.com/wabscale/xv6-public",
        )
    )
    db.session.commit()
    cache.delete_memoized(get_repos)


@with_context
def get_student_id():
    student = User.query.filter(User.netid == "student").first()
    return student.id


def permission_test(
    path,
    fail_for: list = None,
    method="get",
    after: Callable[..., Any] = None,
    **kwargs,
):
    def _test_permission(_path, _fail_for, _method, _after, **_kwargs):
        sessions = {
            "student": Session("student"),
            "ta": Session("ta"),
            "professor": Session("professor"),
            "superuser": Session("superuser"),
        }

        for permission, session in sessions.items():
            if _method == "get":
                request_func = session.get
            elif _method == "post":
                request_func = session.post_json
            else:
                request_func = session.get
            request_func(path, should_fail=permission in _fail_for, **_kwargs)

            if _after is not None:
                _after()

    if fail_for is None:
        fail_for = ["student"]

    return _test_permission(path, fail_for, method, after, **kwargs)


if __name__ == "__main__":

    def test_this_file():
        ts = Session()
        ts.get("/public/auth/whoami")

    run_main(test_this_file)
