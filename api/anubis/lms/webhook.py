from anubis.lms.repos import get_repos
from anubis.models import Assignment, AssignmentRepo, User, db
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


def guess_github_repo_owner(assignment: Assignment, repo_name: str) -> User:
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
    netid1 = "-".join(repo_name_split)
    netid2 = "-".join(repo_name_split[:-1])
    user = User.query.filter(
        User.netid.in_([netid1, netid2]),
        User.netid != "",
    ).first()
    return user


def check_repo(assignment, repo_url, user=None) -> AssignmentRepo:
    """
    While processing the webhook, we need to check to see if we have
    record of the repo. This function takes what it needs to create
    the record of the repo if it didn't already exist.

    :param assignment:
    :param repo_url:
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
            github_username=user.github_username,
        )
        db.session.add(repo)
        db.session.commit()

        if user is not None:
            cache.delete_memoized(get_repos, user.id)

    # Return the repo object
    return repo
