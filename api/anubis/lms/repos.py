from anubis.models import db, Assignment, AssignmentRepo, Submission, TheiaSession
from anubis.utils.cache import cache
from anubis.utils.data import is_debug, with_context
from sqlalchemy.sql import func, select
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

