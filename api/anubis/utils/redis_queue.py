from redis import Redis
from rq import Queue

from anubis.rpc.pipeline import test_repo
from anubis.rpc.theia import initialize_theia_session


def rpc_enqueue(func, *args):
    """
    Enqueues a job on the redis cache

    :func callable: any callable object
    :args tuple: ordered arguments for function
    """
    with Redis(host='redis') as conn:
        q = Queue(connection=conn)
        q.enqueue(func, *args)


def enqueue_webhook(*args):
    """Enqueues a test job"""
    rpc_enqueue(
        test_repo,
        *args
    )


def enqueue_ide_initialize(*args):
    """Enqueue an ide initialization job"""

    rpc_enqueue(initialize_theia_session, *args)
