from anubis.utils.auth import create_token
from anubis.models import db, User
from anubis.app import create_app
import traceback
import requests
import hashlib
import random
import string
import json
import sys
import os
import functools

os.environ["DEBUG"] = "1"
os.environ["DISABLE_ELK"] = "1"
os.environ["DB_HOST"] = "127.0.0.1"
os.environ["CACHE_REDIS_HOST"] = "127.0.0.1"


def initialize_env():
    os.environ['DB_HOST'] = '127.0.0.1'
    os.environ['REDIS_HOST'] = '127.0.0.1'
    os.environ['DISABLE_ELK'] = '1'
    os.environ['DEBUG'] = '1'

    test_root = os.path.dirname(__file__)
    api_root = os.path.dirname(test_root)

    if test_root not in sys.path:
        sys.path.append(test_root)

    if api_root not in sys.path:
        sys.path.append(api_root)


def app_context(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        initialize_env()

        from anubis.app import create_app
        app = create_app()

        with app.app_context():
            return func(*args, **kwargs)

    return wrapper


@app_context
def do_seed():
    from anubis.rpc.seed import seed_main
    seed_main()


def format_exception(e: Exception):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(
        traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])
    )

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)

    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str


def print_full_error(e, r):
    print("Printing only the traceback above the current stack frame")
    print(
        "".join(
            traceback.format_exception(
                sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]
            )
        )
    )
    print()
    print("Printing the full traceback as if we had not caught it here...")
    print()
    format_exception(e)
    print(r.text)
    print(f"status_code={r.status_code}")
    print(r.url)
    exit(1)


def _create_user_session(url: str, name: str, netid: str, admin: bool, superuser: bool):
    """
    Create a new user on the backend

    :return: requests session
    """

    # Create user in db
    user = User(
        netid=netid,
        name=name,
        github_username=netid,
        is_admin=admin,
        is_superuser=superuser,
    )
    db.session.add(user)
    db.session.commit()

    # Get user token
    token = create_token(netid)

    # Create requests session
    session = requests.session()
    session.cookies["token"] = token
    r = session.get(url + "/public/auth/whoami")

    try:
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["data"] is not None
        assert data["error"] is None
    except AssertionError as e:
        print_full_error(e, r)
    return session


def create_name() -> str:
    name_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "names.json"
    )
    name_file = open(name_file_path)
    names = json.load(name_file)

    return f"{random.choice(names)} {random.choice(names)}"


def create_netid(name: str) -> str:
    initials = "".join(word[0].lower() for word in name.split())
    numbers = "".join(random.choice(string.digits) for _ in range(3))

    return f"{initials}{numbers}"


class TestSession(object):
    """
    This object will provide you with a functioning test session with
    a ransom user set up with it. You can call the get and post functions
    to move data between the session and the api.

    test_session = TestSession()
    data = test_session.get('/api/auth/whoami')
    # data ->> {'email': 'test.abcyf.1@pc.email', ...}
    """

    def __init__(
        self, domain: str = "localhost", port: int = 80, admin=False, superuser=False
    ):
        self.url = f"http://{domain}:{port}/api"
        self.timings = []
        self.name = create_name()
        self.netid = create_netid(self.name)
        self._session = _create_user_session(
            self.url, self.name, self.netid, admin, superuser
        )

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


if __name__ == "__main__":

    def test_this_file():
        ts = TestSession()
        ts.get("/public/auth/whoami")

    run_main(test_this_file)
