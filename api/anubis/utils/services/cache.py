from flask_caching import Cache

cache = Cache(config={"CACHE_TYPE": "redis"})


@cache.memoize(timeout=1)
def cache_health():
    """TODO"""
    return None
