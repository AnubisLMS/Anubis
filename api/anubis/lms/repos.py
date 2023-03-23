from sqlalchemy.sql import func, select, and_

from anubis.models import db, Assignment, AssignmentRepo, Submission, User
from anubis.utils.cache import cache
from anubis.utils.data import is_debug, is_job, with_context
from anubis.utils.logging import logger, verbose_call


@cache.memoize(timeout=10, source_check=True, unless=is_debug)
def get_repos(user_id: str):
    repos: list[AssignmentRepo] = (
        AssignmentRepo.query.join(Assignment)
        .filter(AssignmentRepo.owner_id == user_id)
        .order_by(Assignment.release_date.desc())
        .all()
    )

    return [repo.data for repo in repos]


@with_context
@verbose_call()
def reap_duplicate_repos():
    repos: list[AssignmentRepo] = (
        AssignmentRepo.query
        .filter(AssignmentRepo.repo_url.in_(
            select(AssignmentRepo.repo_url)
            .group_by(AssignmentRepo.repo_url)
            .having(func.count(AssignmentRepo.id) > 1)
        ))
        .order_by(AssignmentRepo.repo_url, AssignmentRepo.created)
        .all()
    )

    # repo_url -> [AssignmentRepo]
    repos_map: dict[str, list[AssignmentRepo]] = {
        repo.repo_url: []
        for repo in repos
    }
    for repo in repos:
        logger.info(f'Found duplicated repo {repo.id=} {repo.repo_url=}')
        repos_map[repo.repo_url].append(repo)

    for repo_url, repos in repos_map.items():
        repos = list(sorted(repos, key=lambda repo: repo.created, reverse=True))

        # Figure out which to keep, which to delete
        newest_repo = repos[0]
        repos_to_delete = repos[1:]

        # Update submissions and delete repo
        for repo in repos_to_delete:
            logger.info(f'Updating submissions for {repo.id=}')
            Submission.query.filter(
                Submission.assignment_repo_id == repo.id
            ).update({'assignment_repo_id': newest_repo.id})

            logger.info(f'Deleting repo {repo.id=}')
            AssignmentRepo.query.filter(AssignmentRepo.id == repo.id).delete()

        # Commit update and delete
        db.session.commit()


@cache.memoize(timeout=-1, unless=is_debug, forced_update=is_job)
def list_repos_with_latest_commit(assignment_id: int) -> list[AssignmentRepo]:
    """
    Calculate the latest accepted submissions for a given assignment,
    and return their corresponding assignment repos.

    This only has a single query that might take some time.
    So we lightly cache it just in case.

    :return: A list a AssignmentRepo's
    """
    # Use a subquery to find the maximum time when the latest accepted submission
    # for each assignment repo, respectively.
    latest_submissions_subq = (
        Submission.query.filter(Submission.assignment_id == assignment_id, Submission.accepted == True)
        .with_entities(
            Submission.assignment_repo_id,
            Submission.accepted,
            func.max(Submission.created).label("created"),
        )
        .group_by(Submission.assignment_repo_id)
        .subquery("subq")
    )

    # Given the time the latest submissions are created, join AssignmentRepo (automatically by sqlalchemy)
    # with the information on their corresponding latest submission.
    submissions = Submission.query.join(
        latest_submissions_subq,
        and_(
            Submission.assignment_repo_id == latest_submissions_subq.c.assignment_repo_id,
            Submission.created == latest_submissions_subq.c.created,
        ),
    ).subquery("subq")

    repos = AssignmentRepo.query.join(
        # Join here so that we can access owner.name
        AssignmentRepo.owner
        # Do an outerjoin so that repos without submissions also get listed.
        # This also allows access to the latest submission via the main query's result.
    ).outerjoin(submissions).with_entities(
        AssignmentRepo.id,
        AssignmentRepo.repo_url,
        AssignmentRepo.netid,
        AssignmentRepo.owner_id,
        User.name.label("owner_name"),
        submissions.c.commit.label("commit"),
        # Because this gets outer joined with the latest submissions, the assignment.id contraint
        # we applied for the submissions need to be reapplied here.
    ).filter(
        AssignmentRepo.assignment_id == assignment_id
    )

    return repos.all()
