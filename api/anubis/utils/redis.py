from redis import Redis
from anubis.env import env

match env.CACHE_TYPE:
    case "RedisCache":
        redis = Redis(
            host=env.CACHE_REDIS_HOST,
            password=env.CACHE_REDIS_PASSWORD,
        )
    case _:
        redis = None
