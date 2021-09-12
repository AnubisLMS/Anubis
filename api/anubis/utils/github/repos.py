import traceback
from typing import List, Optional
from parse import parse

from anubis.models import User, Assignment, AssignmentRepo, db, Submission, SubmissionBuild, SubmissionTestResult
from anubis.utils.github.api import github_graphql, github_rest
from anubis.utils.services.logger import logger


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
    return github_rest(f'/repos/{github_org}/{new_repo_name}/collaborators/{github_username}', {
        'permission': 'push',
    }, method='put')


def assignment_repo_name(user: User, assignment: Assignment) -> str:
    # Get assignment name (lowercase and spaces removed)
    assignment_name = assignment.name.lower().replace(' ', '-')

    # Create a repo name from assignment name, unique code and github username
    new_repo_name = f'{assignment_name}-{assignment.unique_code}-{user.github_username}'

    return new_repo_name


def assignment_repo_url(user: User, assignment: Assignment) -> str:
    # Create a repo url from assignment name, unique code and github username
    new_repo_name = assignment_repo_name(user, assignment)

    github_org = assignment.course.github_org
    new_repo_url = f'https://github.com/{github_org}/{new_repo_name}'

    return new_repo_url


def delete_assignment_repo(user: User, assignment: Assignment):
    # Get template information
    github_org = assignment.course.github_org

    # Get a generated assignment repo name
    new_repo_name = assignment_repo_name(user, assignment)

    # Try to get the assignment repo from the database
    repo: AssignmentRepo = AssignmentRepo.query.filter(
        AssignmentRepo.assignment_id == assignment.id,
        AssignmentRepo.owner_id == user.id,
    ).first()

    repo_name = new_repo_name

    if repo is not None:
        # Fetch all submissions for the student
        submissions: List[Submission] = Submission.query.filter(
            Submission.assignment_id == assignment.id,
            Submission.assignment_repo_id == repo.id,
        ).all()
        submission_ids = list(map(lambda x: x.id, submissions))

        # Go through all the submissions, deleting builds
        # and tests as we go
        SubmissionBuild.query.filter(
            SubmissionBuild.submission_id.in_(submission_ids)
        ).delete()
        SubmissionTestResult.query.filter(
            SubmissionTestResult.submission_id.in_(submission_ids)
        ).delete()

        # Delete submissions themselves
        Submission.query.filter(
            Submission.id.in_(submission_ids),
        ).delete()

        # Parse out github org and repo_name from url before deletion
        github_org, repo_name = parse('https://github.com/{}/{}', repo.repo_url)

        # Delete the repo
        AssignmentRepo.query.filter(AssignmentRepo.id == repo.id).delete()

        # Commit the deletes
        db.session.commit()

    try:
        # Make the github api call to delete the repo on github
        r = github_rest(f'/repos/{github_org}/{repo_name}', method='delete')
        logger.error(r)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f'Failed to delete repo {e}')
        logger.error(f'continuing')


def create_assignment_repo(user: User, assignment: Assignment) -> AssignmentRepo:
    # Get template information
    template_repo_path = assignment.github_template
    github_org = assignment.course.github_org

    # Get a generated assignment repo name
    new_repo_name = assignment_repo_name(user, assignment)
    new_repo_url = assignment_repo_url(user, assignment)

    # Try to get the assignment repo from the database
    repo: AssignmentRepo = AssignmentRepo.query.filter(
        AssignmentRepo.assignment_id == assignment.id,
        AssignmentRepo.owner_id == user.id,
    ).first()

    # If repo does not exist yet, create one
    if repo is None:
        repo = AssignmentRepo(
            assignment_id=assignment.id,
            owner_id=user.id,
            github_username=user.github_username,
            repo_url=new_repo_url,
        )
        db.session.add(repo)
        db.session.commit()

    if repo.repo_url != new_repo_url:
        repo.repo_url = new_repo_url
        db.session.commit()

    try:
        # If repo has not been created yet
        if not repo.repo_created:

            # We need to use some of github's internal ID values
            # for creating a repo from the template.
            data = get_github_template_ids(template_repo_path, github_org)

            # If the response was None, the api request failed
            if data is None:
                return repo

            # Get organization and template repo IDs
            owner_id = data['organization']['id']
            template_repo_id = data['repository']['id']

            # Try to create the student's assignment repo from the template
            # using the github graphql api.
            data = create_repo_from_template(owner_id, template_repo_id, new_repo_name)

            # If the response was None, the api request failed
            if data is None:
                logger.error('Create repo failed')
                return repo

            # Mark the repo as created
            repo.repo_created = True
            db.session.commit()
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f'Failed to create repo {e}')
        logger.error(f'continuing')

    try:
        # If repo has not been configured
        if not repo.collaborator_configured:

            # Use github REST api to to add the student as a collaborator
            # to the repo.
            data = add_collaborator(github_org, new_repo_name, user.github_username)

            # If the response was None, the api request failed
            if data is None:
                logger.error('Failed to set permissions')
                return repo

            # Mark the repo as collaborator configured
            repo.collaborator_configured = True
            db.session.commit()
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f'Failed to configure collaborators {e}')
        logger.error(f'continuing')

    return repo
