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

def test_update_committer_info():
    s = Session("student")

    # Attempt to set committer info
    expected_name = "Test User"
    expected_email = "test@example.com"
    s.patch_json(
        "/public/profile/update-committer-info",
        json={
            "committer_name": expected_name,
            "committer_email": expected_email,
        }
    )
    user = s.get("/public/auth/whoami")["user"]
    assert user["committer_name"] == expected_name
    assert user["committer_email"] == expected_email


    # Attempt to unset committer info
    s.patch_json(
        "/public/profile/update-committer-info",
        json={
            "committer_name": "",
            "committer_email": "",
        }
    )
    user = s.get("/public/auth/whoami")["user"]
    assert user["committer_name"] == None
    assert user["committer_email"] == None
