from typing import List

from anubis.utils.data import with_context


@with_context
def make_shared_assignment(assignment_id: str, group_netids: List[List[str]]):
    from anubis.lms.assignments import make_shared_assignment as make_shared_assignment_

    make_shared_assignment_(assignment_id, group_netids)
