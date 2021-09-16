from typing import List

from anubis.models import AssignmentRepo, Assignment
from anubis.utils.data import is_debug
from anubis.utils.cache import cache


@cache.memoize(timeout=10, source_check=True, unless=is_debug)
def get_repos(user_id: str):
    repos: List[AssignmentRepo] = (
        AssignmentRepo.query.join(Assignment)
            .filter(AssignmentRepo.owner_id == user_id)
            .order_by(Assignment.release_date.desc())
            .all()
    )

    return [repo.data for repo in repos]
