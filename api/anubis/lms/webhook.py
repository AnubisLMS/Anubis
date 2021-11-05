from anubis.lms.repos import get_repos
from anubis.models import AssignmentRepo, User, db
from anubis.utils.cache import cache


def parse_webhook(webhook):
    """
    Parse out some of the important basics of any webhook.

    :param webhook:
    :return:
    """

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
    """
    In order to match a webhook to a user, we need to know the github username
    that the repo in question was made for. The github username is in the name
    of the repo.

    This function takes the name of the repo, and does some parsing tricks to
    take a fairly confident guess as to what the github username is.

    :param assignment:
    :param repo_name:
    :return:
    """
    repo_name_split = repo_name.split("-")
    unique_code_index = repo_name_split.index(assignment.unique_code)
    repo_name_split = repo_name_split[unique_code_index + 1 :]
    github_username1 = "-".join(repo_name_split)
    github_username2 = "-".join(repo_name_split[:-1])
    user = User.query.filter(
        User.github_username.in_([github_username1, github_username2]),
        User.github_username != "",
    ).first()

    github_username_guess = github_username1
    if user is None:
        if any(github_username_guess.endswith(i) for i in ["-1", "-2", "-3"]):
            github_username_guess = github_username2
    else:
        github_username_guess = user.github_username

    return user, github_username_guess


def check_repo(assignment, repo_url, github_username, user=None) -> AssignmentRepo:
    """
    While processing the webhook, we need to check to see if we have
    record of the repo. This function takes what it needs to create
    the record of the repo if it didn't already exist.

    :param assignment:
    :param repo_url:
    :param github_username:
    :param user:
    :return:
    """

    # if the user is not None, then the submission is
    # not dangling.
    if user is not None:
        repo = AssignmentRepo.query.filter(
            AssignmentRepo.assignment_id == assignment.id,
            AssignmentRepo.owner == user,
        ).first()

    # If the user is None, then the submission is
    # dangling.
    else:
        repo = AssignmentRepo.query.filter(AssignmentRepo.repo_url == repo_url).first()

    # If the repo did not exist, then create it.
    if repo is None:
        repo = AssignmentRepo(
            owner=user,
            assignment=assignment,
            repo_url=repo_url,
            github_username=github_username,
        )
        db.session.add(repo)
        db.session.commit()

        if user is not None:
            cache.delete_memoized(get_repos, user.id)

    # Return the repo object
    return repo
