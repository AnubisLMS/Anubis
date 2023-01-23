from pottery import Redlock
from redis import Redis

from anubis.env import env

match env.CACHE_TYPE:
    case "RedisCache":
        redis = Redis(
            host=env.REDIS_HOST,
            password=env.REDIS_PASS,
        )
    case _:
        redis = None


def create_redis_lock(key: str, auto_release_time: float = 3.0) -> Redlock:
    lock = Redlock(
        key=key,
        masters={redis},
        auto_release_time=auto_release_time,
    )
    return lock
