"""
This is where we should implement any and all job function for the
redis queue. The rq library requires special namespacing in order to work,
so these functions must reside in a separate file.
"""

import traceback

from redis import Redis
from rq import Queue

from anubis.env import env
from anubis.rpc.assignments import make_shared_assignment
from anubis.rpc.lms import assign_missing_questions
from anubis.rpc.pipeline import create_submission_pipeline, reap_stale_submission_pipelines
from anubis.rpc.seed import seed
from anubis.rpc.theia import initialize_theia_session, reap_theia_session_by_id, reap_stale_theia_sessions


def rpc_enqueue(func, queue=None, args=None):
    """
    Enqueues a job on the redis cache

    :func callable: any callable object
    :args tuple: ordered arguments for function
    """

    # Set defaults
    if queue is None:
        queue = "default"
    if args is None:
        args = tuple()

    # If we are running in mindebug, there is
    # no rq cluster to send things off to.
    if env.MINDEBUG:
        try:
            return func(*args)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return

    with Redis(host=env.CACHE_REDIS_HOST, password=env.CACHE_REDIS_PASSWORD) as conn:
        q = Queue(name=queue, connection=conn)
        q.enqueue(func, *args)
        conn.close()


def enqueue_autograde_pipeline(*args, queue: str = "regrade"):
    """Enqueues a test job"""
    rpc_enqueue(create_submission_pipeline, queue=queue, args=args)


def enqueue_ide_initialize(*args):
    """Enqueue an ide initialization job"""
    rpc_enqueue(initialize_theia_session, queue="theia", args=args)


def enqueue_ide_stop(*args):
    """Reap theia session kube resources"""
    rpc_enqueue(reap_theia_session_by_id, queue="theia", args=args)


def enqueue_ide_reap_stale(*args):
    """Reap stale ide resources"""
    rpc_enqueue(reap_stale_theia_sessions, queue="theia", args=args)


def enqueue_pipeline_reap_stale(*args):
    """Reap stale pipeline job resources"""
    rpc_enqueue(reap_stale_submission_pipelines, queue="theia", args=args)


def enqueue_seed():
    """Enqueue debug seed data"""
    rpc_enqueue(seed, queue="default")


def enqueue_assign_missing_questions(*args):
    """Enqueue assign missing questions"""
    rpc_enqueue(assign_missing_questions, queue="default", args=args)


def enqueue_make_shared_assignment(*args):
    """Enqueue make shared assignment"""
    rpc_enqueue(make_shared_assignment, queue="default", args=args)
