from redis import Redis
from rq import Queue

from anubis.rpc import test_repo


def rpc_enqueue(func, *args):
    """
    Enqueues a job on the redis cache

    :func callable: any callable object
    :args tuple: ordered arguments for function
    """
    with Redis(host='redis') as conn:
        q = Queue(connection=conn)
        q.enqueue(func, *args)


def enqueue_webhook_rpc(*args):
    """
    Enqueues a test job

    :repo_url str: github repo url (eg https://github.com/os3224/...)
    """
    rpc_enqueue(
        test_repo,
        *args
    )
