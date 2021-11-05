from utils import Session

from anubis.utils.data import rand


def test_profile_public():
    s = Session("student")

    s.get(
        "/public/profile/set-github-username",
        params={"github_username": "professor"},
        should_fail=True,
    )

    s.get(
        "/public/profile/set-github-username",
        params={"github_username": rand(8)},
    )
