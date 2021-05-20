from typing import List

from anubis.models import AssignmentRepo, Assignment
from anubis.utils.services.cache import cache
from anubis.utils.data import is_debug


@cache.memoize(timeout=3600, source_check=True, unless=is_debug)
def get_repos(user_id: str):
    repos: List[AssignmentRepo] = (
        AssignmentRepo.query.join(Assignment)
            .filter(AssignmentRepo.owner_id == user_id)
            .distinct(AssignmentRepo.repo_url)
            .order_by(Assignment.release_date.desc())
            .all()
    )

    return [repo.data for repo in repos]