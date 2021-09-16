from datetime import datetime, timedelta
from typing import List

from sqlalchemy.sql import or_

from anubis.models import (
    db,
    User,
    Assignment,
    Submission,
    AssignmentRepo,
)
from anubis.utils.github.api import github_graphql
from anubis.utils.github.repos import create_assignment_repo
from anubis.utils.logging import logger


def fix_github_broken_repos():
    # Search for broken repos
    broken_repos: List[AssignmentRepo] = AssignmentRepo.query.filter(or_(
        # Repo not created
        AssignmentRepo.repo_created == False,

        # Collaborator not configured
        AssignmentRepo.collaborator_configured == False,
    ),
        AssignmentRepo.created > datetime.now() + timedelta(minutes=1),
        AssignmentRepo.created < datetime.now() - timedelta(hours=1),
    ).all()

    # Iterate over broken repos, fixing as we go
    for repo in broken_repos:

        # Get student & assignment
        student: User = repo.owner
        assignment: Assignment = repo.assignment

        # Log fix event
        logger.info(f'Attempting to fix broken repo netid={student.netid} assignment={assignment.unique_code}')

        # The create assignment repo function will attempt
        # to fix missing steps.
        create_assignment_repo(student, assignment)


def fix_github_missing_submissions(org_name: str):
    from anubis.lms.submissions import init_submission
    from anubis.lms.webhook import check_repo, guess_github_username
    from anubis.utils.rpc import enqueue_autograde_pipeline

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