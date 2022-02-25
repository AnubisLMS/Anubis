import functools

from anubis.utils.data import is_job


def create_repo_safety_net(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        repos, errors = func(*args, **kwargs)
        if len(errors) > 0 and not is_job():
            from anubis.rpc.enqueue import enqueue_create_assignment_github_repo
            enqueue_create_assignment_github_repo(*args)
        return repos, errors

    return wrapper
