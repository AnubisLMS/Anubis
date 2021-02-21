from anubis.models import db, User, AssignmentRepo
from anubis.utils.logger import logger
from sqlalchemy import or_


def parse_webhook(webhook):
    # Load the basics from the webhook
    repo_url = webhook["repository"]["url"]
    repo_name = webhook["repository"]["name"]
    pusher_username = webhook["pusher"]["name"]
    commit = webhook["after"]
    before = webhook["before"]
    ref = webhook["ref"]

    return (
        repo_url,
        repo_name,
        pusher_username,
        commit,
        before,
        ref,
    )


def guess_github_username(assignment, repo_name):
    repo_name_split = repo_name.split("-")
    unique_code_index = repo_name_split.index(assignment.unique_code)
    repo_name_split = repo_name_split[unique_code_index + 1:]
    github_username1 = "-".join(repo_name_split)
    github_username2 = "-".join(repo_name_split[:-1])
    user = User.query.filter(
        User.github_username.in_([github_username1, github_username2]),
        User.github_username != ''
    ).first()

    github_username_guess = github_username1
    if user is None:
        if any(github_username_guess.endswith(i) for i in ['-1', '-2', '-3']):
            github_username_guess = github_username2
    else:
        github_username_guess = user.github_username

    return user, github_username_guess


def check_repo(assignment, repo_url, github_username, user=None):
    if user is not None:
        repo = AssignmentRepo.query.filter(
            AssignmentRepo.assignment_id == assignment.id,
            AssignmentRepo.owner == user,
        ).first()
    else:
        repo = AssignmentRepo.query.filter(
            AssignmentRepo.repo_url == repo_url
        ).first()

    if repo is None:
        repo = AssignmentRepo(
            owner=user,
            assignment=assignment,
            repo_url=repo_url,
            github_username=github_username,
        )
        db.session.add(repo)
        db.session.commit()

    return repo