from flask_caching import Cache

cache = Cache(config={"CACHE_TYPE": "redis"})


@cache.memoize(timeout=1)
def cache_health():
    """
    This simple function is used to do health checks
    on the cache (redis specifically). If this function
    fails, then redis is probably failing.

    :return:
    """
    return None
