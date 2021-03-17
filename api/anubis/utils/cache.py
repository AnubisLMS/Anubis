from flask_caching import Cache

cache = Cache(config={"CACHE_TYPE": "redis"})


@cache.cached(timeout=1)
def cache_health():
    pass
