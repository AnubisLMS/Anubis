import docker

"""
This is where we should implement any and all job function for the
redis queue. The rq library requires specical namespacing in order to work,
so these functions must reside in a seperate file.
"""


def test_repo(repo_url, netid, assignment_name):
    """
    This function should launch the apropriate testing container
    for the assignment, passing along the function arguments.
    """

    client = docker.from_env()
    client.containers.run(
        'os3224-{}'.format(assignment_name),
        [repo_url, netid, assignment_name],
        detach=True,
        remove=True,
        network='traefik-proxy',
        privileged=True,
    )


