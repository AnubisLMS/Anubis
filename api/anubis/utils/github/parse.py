from typing import Optional

from parse import parse


def parse_github_org_name(org_url: str) -> Optional[str]:
    """
    Get org name from a github url

    "https://github.com/os3224" -> "os3224"

    """
    r = parse("https://github.com/{}", org_url)

    if r is None:
        return ''

    return r[1].strip().rstrip('/')


def parse_github_repo_name(repo_url: str) -> Optional[str]:
    """
    Get github repo name from https url.

    parse_github_repo_name("https://github.com/GusSand/Anubis")
    -> "Anubis"

    :param repo_url:
    :return:
    """
    r = parse("https://github.com/{}/{}", repo_url)

    if r is None:
        return ''

    return r[1]