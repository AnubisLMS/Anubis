from datetime import datetime

from sqlalchemy.sql import distinct

from anubis.models import db, Submission, TheiaSession, User
from anubis.utils.cache import cache
from anubis.utils.data import is_debug, is_job


def _get_active_ids(Model, day_start: datetime, day_end: datetime) -> list[str]:
    active_owner_ids: list[str] = db.session.query(
        distinct(Model.owner_id)
    ).filter(
        Model.created >= day_start,
        Model.created <= day_end,
    ).all()
    return list(map(lambda x: x[0], active_owner_ids))


def _get_day_start_end(day: datetime = None, end_day: datetime = None) -> tuple[datetime, datetime]:
    if day is None:
        day = datetime.now()
    day_start = day.replace(hour=0, second=0, microsecond=0)

    if end_day is None:
        end_day = day
    day_end = end_day.replace(hour=23, second=59, microsecond=0)

    return day_start, day_end


@cache.memoize(timeout=60, source_check=True, unless=is_debug, forced_update=is_job)
def get_active_theia_users(day: datetime = None, end_day: datetime = None) -> set[str]:
    day_start, day_end = _get_day_start_end(day, end_day)
    active_owner_ids = _get_active_ids(TheiaSession, day_start, day_end)
    return set(active_owner_ids)


@cache.memoize(timeout=60, source_check=True, unless=is_debug, forced_update=is_job)
def get_active_submission_users(day: datetime = None, end_day: datetime = None) -> set[str]:
    day_start, day_end = _get_day_start_end(day, end_day)
    active_owner_ids = _get_active_ids(Submission, day_start, day_end)
    return set(active_owner_ids)


@cache.memoize(timeout=60, source_check=True, unless=is_debug, forced_update=is_job)
def get_platform_users(day: datetime = None) -> int:
    return User.query.filter(
        User.created < day,
    ).count()
