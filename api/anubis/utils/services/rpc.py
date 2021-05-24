from redis import Redis
from rq import Queue

from anubis.config import config
from anubis.rpc.pipeline import create_submission_pipeline
from anubis.rpc.seed import seed
from anubis.rpc.theia import (
    initialize_theia_session,
    reap_theia_session_by_id,
    reap_stale_theia_sessions,
)
from anubis.rpc.visualizations import create_visuals as create_visuals_


def rpc_enqueue(func, queue=None, args=None):
    """
    Enqueues a job on the redis cache

    :func callable: any callable object
    :args tuple: ordered arguments for function
    """
    if queue is None:
        queue = 'default'
    if args is None:
        args = tuple()
    with Redis(host=config.CACHE_REDIS_HOST, password=config.CACHE_REDIS_PASSWORD) as conn:
        q = Queue(name=queue, connection=conn)
        q.enqueue(func, *args)
        conn.close()


def enqueue_autograde_pipeline(*args, queue: str = 'default'):
    """Enqueues a test job"""
    rpc_enqueue(create_submission_pipeline, queue=queue, args=args)


def enqueue_ide_initialize(*args):
    """Enqueue an ide initialization job"""
    rpc_enqueue(initialize_theia_session, queue='theia', args=args)


def enqueue_ide_stop(*args):
    """Reap theia session kube resources"""
    rpc_enqueue(reap_theia_session_by_id, queue='theia', args=args)


def enqueue_ide_reap_stale(*args):
    """Reap stale ide resources"""
    rpc_enqueue(reap_stale_theia_sessions, queue='theia', args=args)


def enqueue_seed():
    """Enqueue debug seed data"""
    rpc_enqueue(seed, queue='default')


def enqueue_create_visuals(*_):
    """Enqueue create visuals"""
    rpc_enqueue(create_visuals_, queue='default')
