from datetime import datetime, timedelta

import sqlalchemy.exc
from sqlalchemy.sql import or_

from anubis.github.api import github_graphql
from anubis.github.repos import create_assignment_student_repo
from anubis.models import Assignment, AssignmentRepo, Submission, User, db
from anubis.utils.logging import logger


def fix_github_broken_repos():
    # Search for broken repos
    broken_repos: list[AssignmentRepo] = AssignmentRepo.query.filter(
        or_(
            # Repo not created
            AssignmentRepo.repo_created == False,
            # Collaborator not configured
            AssignmentRepo.collaborator_configured == False,
            # Tas not configured
            AssignmentRepo.ta_configured == False,
        ),
        AssignmentRepo.created <= datetime.now() + timedelta(minutes=1),
        AssignmentRepo.created >= datetime.now() - timedelta(hours=1),
    ).all()

    # Iterate over broken repos, fixing as we go
    for repo in broken_repos:
        # Get student & assignment
        student: User = repo.owner
        assignment: Assignment = repo.assignment

        # Log fix event
        logger.info(f"Attempting to fix broken repo netid={student.netid} assignment={assignment.unique_code}")

        # The create assignment repo function will attempt
        # to fix missing steps.
        create_assignment_student_repo(student, assignment)


def fix_github_missing_submissions(org_name: str):
    from anubis.lms.submissions import init_submission
    from anubis.lms.webhook import check_repo, guess_github_repo_owner
    from anubis.rpc.enqueue import enqueue_autograde_pipeline

    # Do graphql nonsense
    # Refer to here for graphql over https: https://graphql.org/learn/serving-over-http/
    query = """
    query githubCommits($orgName: String!, $first: Int!, $after: String) {
      organization(login: $orgName) {
        repositories(after: $after, first: $first, orderBy: {field: CREATED_AT, direction: DESC}) {
          pageInfo {
            endCursor
          }
          nodes {
            defaultBranchRef {
              target {
                ... on Commit {
                  history(first: 20) {
                    edges {
                      node {
                        oid
                      }
                    }
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
    """

    query_size: int = 10
    after = None
    for _ in range(20):
        # Make the github query
        data = github_graphql(query, {"orgName": org_name, "first": query_size, "after": after})

        # Check that the data is there
        if data is None:
            logger.error(f'Invalid response from github')
            return

        # Get organization and repositories from response
        organization = data["organization"]
        repositories = organization["repositories"]["nodes"]
        after = organization["repositories"]["pageInfo"]["endCursor"]

        # Running map of unique_code -> assignment objects
        assignments = dict()

        # Parse out repo name and url from graphql response
        repos = map(lambda node: (node["name"], node["url"], node["defaultBranchRef"]), repositories)
        for repo_name, repo_url, ref in repos:
            assignment = None

            # Try to get the assignment object from running map
            for code in repo_name.split("-"):
                assignment = assignments.get(code, None)

            # If not in the map, then try to get from the database
            if assignment is None:
                assignment = Assignment.query.filter(Assignment.unique_code.in_(repo_name.split("-"))).first()

                if assignment is not None:
                    assignments[assignment.unique_code] = assignment

            # If not in database or map, then eject
            if assignment is None:
                print(f"Could not find assignment for {repo_name}")
                continue

            # Guess github username, then create the repo if it doesn't yet exist
            user, netid = guess_github_repo_owner(assignment, repo_name)
            repo = check_repo(assignment, repo_url, user, user.netid)

            if user is None:
                continue

            # Check for missing submissions
            try:
                for commit in map(lambda x: x["node"]["oid"], ref["target"]["history"]["edges"]):
                    submission = Submission.query.filter(Submission.commit == commit).first()
                    if submission is None:
                        print(f"Found missing submission {user.netid=} {assignment=} {commit=}")
                        try:
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
                            if submission.assignment.autograde_enabled:
                                enqueue_autograde_pipeline(submission.id)
                        except sqlalchemy.exc.IntegrityError:
                            db.session.rollback()
                            logger.warning(f'Failed to create submission that already exists {user.netid=} {assignment=} {commit=}')
            except TypeError as e:
                logger.warning(f'Failed to parse commit objects for repo - {e} - {str(repo)}')

            r = AssignmentRepo.query.filter(AssignmentRepo.repo_url == repo_url).first()
            if r is not None:
                if r.owner_id != user.id:
                    print(f"fixing broken repo owner {r.id}")
                    r.owner_id = user.id
                    enqueue_submission_pipelines = []
                    for submission in Submission.query.filter(Submission.assignment_repo_id == r.id).all():
                        submission.owner_id = user.id
                        enqueue_submission_pipelines.append(submission.id)

                    db.session.commit()
                    for sid in enqueue_submission_pipelines:
                        enqueue_autograde_pipeline(sid)

            if repo:
                print(f"checked repo: {repo_name} {user.github_username} {user} {repo.id}")
