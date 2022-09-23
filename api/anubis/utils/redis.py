from redis import Redis
from anubis.env import env

redis = Redis(
    host=env.CACHE_REDIS_HOST,
    password=env.CACHE_REDIS_PASSWORD,
)
