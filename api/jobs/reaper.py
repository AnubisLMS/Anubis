import json
import os
import traceback
from datetime import datetime, timedelta

import requests

from anubis.models import db, Submission, Assignment, AssignmentRepo
from anubis.utils.data import with_context
from anubis.utils.lms.autograde import bulk_autograde
from anubis.utils.lms.submissions import init_submission
from anubis.utils.lms.webhook import check_repo, guess_github_username
from anubis.utils.services.rpc import enqueue_ide_reap_stale, enqueue_autograde_pipeline
from anubis.utils.visuals.assignments import get_assignment_sundial


def reap_stale_submissions():
    """
    This will set find stale submission and set them to processed. A stale
    submission is one that has not been updated in 15 minutes and is still
    in a processing state.

    Flask app context is required before calling this function.

    :return:
    """

    print("Reaping stale submissions")

    # Find and update stale submissions
    Submission.query.filter(
        Submission.last_updated < datetime.now() - timedelta(minutes=60),
        Submission.processed == False,
        Submission.state != 'regrading',
    ).update({
        'processed': True,
        'state': "Reaped after timeout",
    }, False)

    # Commit any changes
    db.session.commit()


def reap_recent_assignments():
    """
    Calculate stats for recent submissions

    :return:
    """
    from anubis.config import config

    recent_assignments = Assignment.query.filter(
        Assignment.release_date > datetime.now(),
        Assignment.due_date > datetime.now() - config.STATS_REAP_DURATION,
    ).all()

    print(json.dumps({
        'reaping assignments:': [assignment.data for assignment in recent_assignments]
    }, indent=2))

    for assignment in recent_assignments:
        for submission in Submission.query.filter(
                Submission.assignment_id == assignment.id,
                Submission.build == None,
        ).all():
            if submission.build is None:
                init_submission(submission)
                enqueue_autograde_pipeline(submission.id)

    for assignment in recent_assignments:
        bulk_autograde(assignment.id)


def reap_broken_repos():
    """
    For reasons not clear to me yet, the webhooks are sometimes missing
    on the first commit. The result is that repos will be created on
    github without anubis seeing them.

    This function should be the fix for this. It will call out to the
    github api to list all the repos under the organization then try to
    create repos for each listed repo.

    :return:
    """
    token = os.environ.get('GITHUB_TOKEN', None)
    if token is None:
        print('MISSING GITHUB_TOKEN')
        return

    # Do graphql nonsense
    query = '''
    query{
      organization(login:"os3224"){
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
    url = 'https://api.github.com/graphql'
    json = {'query': query}
    headers = {'Authorization': 'token %s' % token}

    # Make the graph request over http
    try:
        r = requests.post(url=url, json=json, headers=headers)
        data = r.json()['data']
        organization = data['organization']
        repositories = organization['repositories']['nodes']
    except Exception as e:
        print(traceback.format_exc())
        print(f'Request to github api Failed {e}')
        return

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


@with_context
def reap():
    # Enqueue a job to reap stale ide k8s resources
    enqueue_ide_reap_stale()

    # Reap the stale submissions
    reap_stale_submissions()

    # Reap broken repos
    reap_broken_repos()

    # Reap broken submissions in recent assignments
    reap_recent_assignments()


if __name__ == "__main__":
    print("")
    print("""
             ___
            /   \\\\
       /\\\\ | . . \\\\
     ////\\\\|     ||
   ////   \\\\\\ ___//\\
  ///      \\\\      \\
 ///       |\\\\      |     
//         | \\\\  \\   \\    
/          |  \\\\  \\   \\   
           |   \\\\ /   /   
           |    \\/   /    
           |     \\\\/|     
           |      \\\\|     
           |       \\\\     
           |        |     
           |_________\\  

""")
    reap()
