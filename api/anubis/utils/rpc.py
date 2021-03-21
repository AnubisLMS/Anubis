from redis import Redis
from rq import Queue

from anubis.config import config
from anubis.rpc.pipeline import test_repo
from anubis.rpc.seed import seed_debug
from anubis.rpc.theia import (
    initialize_theia_session,
    reap_theia_session,
    reap_stale_theia_sessions,
)


def rpc_enqueue(func, *args):
    """
    Enqueues a job on the redis cache

    :func callable: any callable object
    :args tuple: ordered arguments for function
    """
    with Redis(host=config.CACHE_REDIS_HOST, password=config.CACHE_REDIS_PASSWORD) as conn:
        q = Queue(connection=conn)
        q.enqueue(func, *args)
        conn.close()


def enqueue_webhook(*args):
    """Enqueues a test job"""
    rpc_enqueue(test_repo, *args)


def enqueue_ide_initialize(*args):
    """Enqueue an ide initialization job"""

    rpc_enqueue(initialize_theia_session, *args)


def enqueue_ide_stop(*args):
    """Reap theia session kube resources"""

    rpc_enqueue(reap_theia_session, *args)


def enqueue_ide_reap_stale(*args):
    """Reap stale ide resources"""
    rpc_enqueue(reap_stale_theia_sessions, *args)


def seed():
    rpc_enqueue(seed_debug, [])
