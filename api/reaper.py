import json
import os
import requests
import traceback
from datetime import datetime, timedelta

from sqlalchemy import func, and_

from anubis.app import create_app
from anubis.models import db, Submission, Assignment, AssignmentRepo, TheiaSession
from anubis.utils.rpc import enqueue_ide_stop, enqueue_ide_reap_stale, enqueue_webhook
from anubis.utils.stats import bulk_stats
from anubis.utils.webhook import check_repo, guess_github_username, parse_webhook


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
        Submission.last_updated < datetime.now() - timedelta(minutes=15),
        Submission.processed == False
    ).update({
        Submission.processed: True,
        Submission.state: "Reaped after timeout"
    }, False)

    # Commit any changes
    db.session.commit()

    print("")


def reap_theia_sessions():
    # Get theia sessions that are older than n hours
    theia_sessions = TheiaSession.query.filter(
        TheiaSession.active == True,
        TheiaSession.last_proxy <= datetime.now() - timedelta(hours=3),
    ).all()

    for theia_session in theia_sessions:
        enqueue_ide_stop(theia_session.id)


def reap_stats():
    from anubis.config import config
    """
    Calculate stats for recent submissions

    :return:
    """
    recent_assignments = Assignment.query.group_by(
        Assignment.course_id
    ).having(
        and_(
            Assignment.release_date == func.max(Assignment.release_date),
            Assignment.release_date > datetime.now() - config.STATS_REAP_DURATION,
        )
    ).all()

    print(json.dumps({
        'reaping assignments:': [assignment.data for assignment in recent_assignments]
    }, indent=2))

    for assignment in recent_assignments:
        bulk_stats(assignment.id)


def reap_repos():
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
    query = 'query{organization(login:"os3224"){repositories(first:100,orderBy:{field:CREATED_AT,direction:DESC}){nodes{name url}}}}'
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
    repos = map(lambda node: (node['name'], node['url']), repositories)
    for repo_name, repo_url in repos:
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

        # submissions = []
        # for submission in Submission.query.filter(Submission.assignment_repo_id == repo.id).all():
        #     if submission.owner_id != user.id:
        #         submission.owner_id = repo.owner_id
        #         submissions.append(submission.id)
        # db.session.commit()
        # for sid in submissions:
        #     enqueue_webhook(sid)

        # r = AssignmentRepo.query.filter(AssignmentRepo.repo_url == repo_url).first()
        # if r is not None:
        #     if r.owner_id != user.id:
        #         print(r.repo_url, user.name)
        #         # r.owner_id = user.id
        #         # submissions = []
        #         # for submission in Submission.query.filter(
        #         #         Submission.assignment_repo_id == r.id
        #         # ).all():
        #         #     submission.owner_id = user.id
        #         #     submissions.append(submission.id)
        #         #
        #         # # db.session.commit()
        #         # for sid in submissions:
        #         #     enqueue_webhook(sid)

        if repo:
            print(f'checked repo: {repo_name} {github_username} {user} {repo.id}')


def reap():
    app = create_app()

    with app.app_context():
        # Reap the stale submissions
        reap_stale_submissions()
        enqueue_ide_reap_stale()
        reap_repos()

        with app.test_request_context():
            # Calculate bulk stats (pre-process stats calls)
            reap_stats()


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
