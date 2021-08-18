import os
import traceback
from typing import Optional, Any, Dict

import requests
from parse import parse

from anubis.utils.services.logger import logger
from anubis.models import db, Submission, Assignment, AssignmentRepo, User


def get_github_token() -> Optional[str]:

    # Get GITHUB token
    token = os.environ.get('GITHUB_TOKEN', None)
    if token is None:
        logger.error('MISSING GITHUB_TOKEN')
        return None
    return token


def github_rest_put(url, body=None):

    token = get_github_token()

    url = 'https://api.github.com' + url
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'token %s' % token,
    }

    try:
        r = requests.put(url, headers=headers, json=body)
        return r.json()
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f'Request to github api Failed {e}')
        return None


def github_graphql(query: str, variables: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:

    # Default values for variables
    if variables is None:
        variables = dict()

    token = get_github_token()

    # Set up request options
    url = 'https://api.github.com/graphql'
    json = {'query': query, 'variables': variables}
    headers = {'Authorization': 'token %s' % token}

    # Make the graph request over http
    try:
        r = requests.post(url=url, json=json, headers=headers)
        return r.json()['data']
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f'Request to github api Failed {e}')
        return None


def get_github_template_ids(template_repo: str, github_org: str):
    id_query = """
    query githubTemplateInfo($orgName: String!, $templateName: String!, $templateOwner: String!) {  
      organization(login: $orgName) {
        id
      }

      repository(name: $templateName, owner: $templateOwner) { 
        id
      }
    }
        """

    p = parse('{}/{}', template_repo)
    github_template_owner, github_template_name = p

    return github_graphql(id_query, {
        'orgName': github_org,
        'templateName': github_template_name,
        'templateOwner': github_template_owner,
    })


def create_repo_from_template(owner_id: str, template_repo_id: str, new_repo_name: str):
    create_query = """
    mutation githubTemplateCreate($ownerId: ID!, $templateRepoId: ID!, $newName: String!) { 
      cloneTemplateRepository(input: {
        ownerId: $ownerId, 
        repositoryId: $templateRepoId,
        name: $newName,
        visibility: PRIVATE,
      }) { 
        repository {
          id
          name
        }
      }
    }    
        """

    return github_graphql(create_query, {
        'ownerId': owner_id,
        'templateRepoId': template_repo_id,
        'newName': new_repo_name,
    })


def add_collaborator(github_org: str, new_repo_name: str, github_username: str):
    return github_rest_put(f'/repos/{github_org}/{new_repo_name}/collaborators/{github_username}', {
        'permission': 'push',
    })


def create_assignment_repo(user: User, assignment: Assignment) -> Optional[AssignmentRepo]:
    template_repo = assignment.template_repo
    github_org = assignment.course.github_org

    assignment_name = assignment.name.lower().replace(' ', '-')
    new_repo_name = f'{assignment_name}-{assignment.unique_code}-{user.github_username}'

    repo: AssignmentRepo = AssignmentRepo.query.filter(
        AssignmentRepo.assignment_id == assignment.id,
        AssignmentRepo.owner_id == user.id,
    ).first()

    if repo is None:
        repo = AssignmentRepo(
            assignment_id=assignment.id,
            owner_id=user.id,
            github_username=user.github_username,
            repo_url=f'https://github.com/{github_org}/{new_repo_name}',
        )
        db.session.add(repo)
        db.session.commit()

    data = get_github_template_ids(template_repo, github_org)
    if data is None:
        return None
    owner_id = data['organization']['id']
    template_repo_id = data['repository']['id']

    if not repo.created:
        data = create_repo_from_template(owner_id, template_repo_id, new_repo_name)
        if data is None:
            logger.error('Create repo failed')
            return
        repo.created = True
        db.session.commit()

    if not repo.collaborator_configured:
        data = add_collaborator(github_org, new_repo_name, user.github_username)
        if data is None:
            logger.error('Failed to set permissions')
            return
        repo.collaborator_configured = True
        db.session.commit()


def fix_github_broken_repos(org_name: str):
    from anubis.utils.lms.submissions import init_submission
    from anubis.utils.lms.webhook import check_repo, guess_github_username
    from anubis.utils.services.rpc import enqueue_autograde_pipeline

    # Do graphql nonsense
    # Refer to here for graphql over https: https://graphql.org/learn/serving-over-http/
    query = '''
    query githubCommits($orgName: String!) {
      organization(login: $orgName){
        repositories(first:100,orderBy:{field:CREATED_AT,direction:DESC}){
          nodes{
            ref(qualifiedName:"master") {
          target {
            ... on Commit {
              history(first: 20) {
                edges { node { oid } }
              }
            }
          }
            }
            name 
            url
          }
        }
      }
    }
    '''

    # Make the github query
    data = github_graphql(query, {'orgName': org_name})

    # Check that the data is there
    if data is None:
        return

    # Get organization and repositories from response
    organization = data['organization']
    repositories = organization['repositories']['nodes']

    # Running map of unique_code -> assignment objects
    assignments = dict()

    # Parse out repo name and url from graphql response
    repos = map(lambda node: (node['name'], node['url'], node['ref']), repositories)
    for repo_name, repo_url, ref in repos:
        assignment = None

        # Try to get the assignment object from running map
        for code in repo_name.split('-'):
            assignment = assignments.get(code, None)

        # If not in the map, then try to get from the database
        if assignment is None:
            assignment = Assignment.query.filter(
                Assignment.unique_code.in_(repo_name.split('-'))
            ).first()

            if assignment is not None:
                assignments[assignment.unique_code] = assignment

        # If not in database or map, then eject
        if assignment is None:
            print(f'Could not find assignment for {repo_name}')
            continue

        # Guess github username, then create the repo if it doesn't yet exist
        user, github_username = guess_github_username(assignment, repo_name)
        repo = check_repo(assignment, repo_url, github_username, user)

        if user is None:
            continue

        # Check for broken submissions
        submissions = []
        for submission in Submission.query.filter(Submission.assignment_repo_id == repo.id).all():
            if submission is None:
                continue
            if submission.owner_id != user.id:
                print(f'found broken submission {submission.id}')
                submission.owner_id = repo.owner_id
                submissions.append(submission.id)
        db.session.commit()
        for sid in submissions:
            enqueue_autograde_pipeline(sid)

        # Check for missing submissions
        for commit in map(lambda x: x['node']['oid'], ref['target']['history']['edges']):
            submission = Submission.query.filter(
                Submission.commit == commit
            ).first()
            if submission is None:
                print(f'found missing submission {github_username} {commit}')
                submission = Submission(
                    commit=commit,
                    owner=user,
                    assignment=assignment,
                    repo=repo,
                    state="Waiting for resources...",
                )
                db.session.add(submission)
                db.session.commit()
                init_submission(submission)
                enqueue_autograde_pipeline(submission.id)

        r = AssignmentRepo.query.filter(AssignmentRepo.repo_url == repo_url).first()
        if r is not None:
            if r.owner_id != user.id:
                print(f'fixing broken repo owner {r.id}')
                r.owner_id = user.id
                submissions = []
                for submission in Submission.query.filter(
                        Submission.assignment_repo_id == r.id
                ).all():
                    submission.owner_id = user.id
                    submissions.append(submission.id)

                db.session.commit()
                for sid in submissions:
                    enqueue_autograde_pipeline(sid)

        if repo:
            print(f'checked repo: {repo_name} {github_username} {user} {repo.id}')


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
