"""
This is where we should implement any and all job function for the
redis queue. The rq library requires special namespacing in order to work,
so these functions must reside in a separate file.
"""

import traceback

from redis import Redis
from rq import Queue

from anubis.env import env
from anubis.github.repos import create_assignment_github_repo
from anubis.ide.initialize import initialize_theia_session
from anubis.k8s.pipeline import create_submission_pipeline
from anubis.k8s.pipeline import reap_pipeline_jobs
from anubis.k8s.theia import reap_theia_session_by_id, reap_stale_theia_sessions
from anubis.lms.assignments import make_shared_assignment
from anubis.lms.questions import assign_missing_questions
from anubis.utils.data import with_context
from anubis.utils.testing.seed import seed


@with_context
def _run_rpc_function(func, *args):
    return func(*args)


def rpc_enqueue(func, queue=None, args=None):
    """
    Enqueues a job on the redis cache

    :func callable: any callable object
    :args tuple: ordered arguments for function
    """

    # set defaults
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
        q.enqueue(_run_rpc_function, func, *args)
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
    rpc_enqueue(reap_pipeline_jobs, queue="theia", args=args)


def enqueue_seed():
    """Enqueue debug seed data"""
    rpc_enqueue(seed, queue="default")


def enqueue_assign_missing_questions(*args):
    """Enqueue assign missing questions"""
    rpc_enqueue(assign_missing_questions, queue="default", args=args)


def enqueue_make_shared_assignment(*args):
    """Enqueue make shared assignment"""
    rpc_enqueue(make_shared_assignment, queue="default", args=args)


def enqueue_create_assignment_github_repo(*args):
    """Enqueue make shared assignment"""
    rpc_enqueue(create_assignment_github_repo, queue="default", args=args)
