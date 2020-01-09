import docker


def get_client():
    return docker.from_env()


