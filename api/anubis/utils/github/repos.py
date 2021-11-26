import traceback
from typing import List

from parse import parse

from anubis.models import Assignment, AssignmentRepo, Submission, SubmissionBuild, SubmissionTestResult, User, db
from anubis.utils.github.api import github_graphql, github_rest
from anubis.utils.logging import logger


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

    p = parse("{}/{}", template_repo)
    github_template_owner, github_template_name = p

    return github_graphql(
        id_query,
        {
            "orgName": github_org,
            "templateName": github_template_name,
            "templateOwner": github_template_owner,
        },
    )


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

    return github_graphql(
        create_query,
        {
            "ownerId": owner_id,
            "templateRepoId": template_repo_id,
            "newName": new_repo_name,
        },
    )


def add_collaborator(github_org: str, new_repo_name: str, github_username: str):
    return github_rest(
        f"/repos/{github_org}/{new_repo_name}/collaborators/{github_username}",
        {
            "permission": "push",
        },
        method="put",
    )


def get_student_assignment_repo_name(user: User, assignment: Assignment) -> str:
    # Get assignment name (lowercase and spaces removed)
    assignment_name = assignment.name.lower().replace(" ", "-")

    # Create a repo name from assignment name, unique code and github username
    new_repo_name = f"{assignment_name}-{assignment.unique_code}-{user.github_username}"

    return new_repo_name


def get_group_assignment_repo_name(users: List[User], assignment: Assignment) -> str:
    # Get assignment name (lowercase and spaces removed)
    assignment_name = assignment.name.lower().replace(" ", "-")

    github_usernames = '-'.join(user.github_username for user in users)

    # Create a repo name from assignment name, unique code and github username
    new_repo_name = f"{assignment_name}-{assignment.unique_code}-{github_usernames}"

    return new_repo_name


def get_student_assignment_repo_url(user: User, assignment: Assignment) -> str:
    # Create a repo url from assignment name, unique code and github username
    new_repo_name = get_student_assignment_repo_name(user, assignment)

    github_org = assignment.course.github_org
    new_repo_url = f"https://github.com/{github_org}/{new_repo_name}"

    return new_repo_url


def get_group_assignment_repo_url(users: List[User], assignment: Assignment) -> str:
    # Create a repo url from assignment name, unique code and github username
    new_repo_name = get_group_assignment_repo_name(users, assignment)

    github_org = assignment.course.github_org
    new_repo_url = f"https://github.com/{github_org}/{new_repo_name}"

    return new_repo_url


def delete_assignment_repo(user: User, assignment: Assignment, commit: bool = True):
    # Get template information
    github_org = assignment.course.github_org

    # Get a generated assignment repo name
    new_repo_name = get_student_assignment_repo_name(user, assignment)

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
        SubmissionBuild.query.filter(SubmissionBuild.submission_id.in_(submission_ids)).delete()
        SubmissionTestResult.query.filter(SubmissionTestResult.submission_id.in_(submission_ids)).delete()

        # Delete submissions themselves
        Submission.query.filter(
            Submission.id.in_(submission_ids),
        ).delete()

        # Parse out github org and repo_name from url before deletion
        github_org, repo_name = parse("https://github.com/{}/{}", repo.repo_url)

        # Delete the repo
        AssignmentRepo.query.filter(AssignmentRepo.id == repo.id).delete(synchronize_session=False)

        if commit:
            # Commit the deletes
            db.session.commit()

    try:
        # Make the github api call to delete the repo on github
        r = github_rest(f"/repos/{github_org}/{repo_name}", method="delete")
        logger.error(r)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"Failed to delete repo {e}")
        logger.error(f"continuing")


def _create_assignment_repo_obj(
    user: User, assignment: Assignment, new_repo_url: str, commit: bool = True
) -> AssignmentRepo:
    """
    Create the database entry for a repo if it does not exist. This function
    does not handle creating the actual github repo on github.

    If the commit parameter is True, then any changes to the database will
    be committed. db.session.commit() will not be called if there are no
    changes though (if the repo already exists for example)

    :param user: Owner of repo
    :param assignment: Assignment for the repo
    :param new_repo_url: generated github URL
    :param commit: commit changes to db or not
    :return: assignment repo object
    """

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
        if commit:
            db.session.commit()

    # If the database entry already exists, but the
    # repo url is different, then update it.
    if repo.repo_url != new_repo_url:
        repo.repo_url = new_repo_url
        if commit:
            db.session.commit()

    return repo


def create_assignment_group_repo(users: List[User], assignment: Assignment) -> List[AssignmentRepo]:
    """
    This function takes a list of users and an assignment, and creates a single
    assignment repo for the group. This will create an AssignmentRepo entry for
    each student, but only one will be returned.

    :param users:
    :param assignment:
    :return:
    """

    # Get a generated assignment repo name
    new_repo_name = get_group_assignment_repo_name(users, assignment)
    new_repo_url = get_group_assignment_repo_url(users, assignment)

    # Create the assignment repo row in the db
    repos: List[AssignmentRepo] = []
    for user in users:
        # Create repo db entry
        repo = _create_assignment_repo_obj(user, assignment, new_repo_url, commit=False)

        # Mark repo as shared
        repo.shared = True

        repos.append(repo)

    db.session.commit()

    # Create the assignment repo
    repos = create_assignment_github_repo(
        repos,
        assignment.github_template,
        assignment.course.github_org,
        new_repo_name,
    )

    return repos


def create_assignment_student_repo(user: User, assignment: Assignment) -> AssignmentRepo:
    # Get a generated assignment repo name
    new_repo_name = get_student_assignment_repo_name(user, assignment)
    new_repo_url = get_student_assignment_repo_url(user, assignment)

    # Create the assignment repo row in the db
    repo = _create_assignment_repo_obj(user, assignment, new_repo_url)

    repos = create_assignment_github_repo(
        [repo],
        assignment.github_template,
        assignment.course.github_org,
        new_repo_name,
    )

    return repos[0]


def create_assignment_github_repo(
    repos: List[AssignmentRepo],
    template_repo_path: str,
    github_org: str,
    new_repo_name: str,
) -> List[AssignmentRepo]:
    """
    Creates an assignment repo and adds collaborators.

    :param repos: AssignmentRepo object
    :param template_repo_path: "wabscale/xv6-public"
    :param github_org: "os3224"
    :param new_repo_name: ""
    :return:
    """

    repo_created = any(repo.repo_created for repo in repos)

    try:
        # If repo has not been created yet
        if not repo_created:

            # We need to use some of github's internal ID values
            # for creating a repo from the template.
            data = get_github_template_ids(template_repo_path, github_org)

            # If the response was None, the api request failed. Also check that
            # some expected values are present in the json data response.
            if data is None and "repository" in data and "id" in data["repository"]:
                for repo in repos:
                    repo.repo_created = False
                db.session.commit()
                return repos

            # Get organization and template repo IDs
            owner_id = data["organization"]["id"]
            template_repo_id = data["repository"]["id"]

            # Try to create the student's assignment repo from the template
            # using the github graphql api.
            data = create_repo_from_template(owner_id, template_repo_id, new_repo_name)

            # If the response was None, the api request failed
            if data is None:
                logger.error("Create repo failed")
                return repos

            # Mark the repo as created
            for repo in repos:
                repo.repo_created = True
            db.session.commit()
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"Failed to create repo {e}")
        logger.error(f"continuing")

    try:

        for repo in repos:

            # If repo has not been configured
            if not repo.collaborator_configured:

                # Get user github username
                collaborator = repo.owner.github_username

                # Use github REST api to to add the student as a collaborator
                # to the repo.
                data = add_collaborator(github_org, new_repo_name, collaborator)

                # Sometimes it takes a moment before we are able to add collaborators to
                # the repo. The message in the response will be Not Found in this situation.
                # We can have it try again to fix.
                if data.get("message", None) == "Not Found":
                    logger.error("Failed to add collaborator (Not Found). Trying again.")
                    data = add_collaborator(github_org, new_repo_name, collaborator)

                # If the response was None, the api request failed
                if data is None or data.get("message", None) == "Not Found":
                    logger.error("Failed to add collaborator")
                    continue

                # Mark the repo as collaborator configured
                repo.collaborator_configured = True
                db.session.commit()
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(f"Failed to configure collaborators {e}")
        logger.error(f"continuing")

    return repos
