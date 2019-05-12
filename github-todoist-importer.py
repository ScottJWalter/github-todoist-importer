import argparse
from github import Github
import os
import todoist


def create_todoist_tasks_from_github_issues(todoist_api_token, todoist_project_name,
                                            github_api_token, github_repo_name, github_assignee):
    # connect to todoist
    todoist_api = todoist.api.TodoistAPI(todoist_api_token)
    todoist_api.sync()

    # Get the ID of the Todoist target project
    project = [p for p in todoist_api.state['projects'] if p['name'] == todoist_project_name][0]

    # connect to github
    github_api = Github(github_api_token)

    # grab the Github repo
    repo = [r for r in github_api.get_user().get_repos() if r.name == github_repo_name][0]

    # loop through the repo issues
    for issue in [i for i in repo.get_issues(state='open', assignee=github_assignee)]:
        print('Processing:  {} into {}'.format(issue.title, project['name']))

        # Create a new Todoist task for the Github issue
        task = todoist_api.items.add(issue.title, project_id=project['id'])

        # Attach a note to the Todoist task with the URL of the issue on Github
        todoist_api.notes.add(task['id'], issue.html_url)

    todoist_api.commit()


def read_args(desc, args):
    """
    We need all 5 arguments, so we look for them first on the command line.  Failing
    that, check for an environment variable of the same name.  If all else fails,
    throw an exception.
    """

    # Build the parser
    parser = argparse.ArgumentParser(description=desc)
    for arg in args:
        # add each argument as a double-dash arg
        parser.add_argument('--{}'.format(arg))

    # parse the command line
    out = parser.parse_args()

    # now, check that each required arg exists
    for arg in args:
        if not eval('out.{}'.format(arg)):
            # if it doesn't exist, look for the environment variable
            if os.environ[arg]:
                eval('out.{} = "{}"'.format(arg, os.environ[arg]))
            else:
                # can't be found.  Error out
                raise Exception('Missing required parameter:  {}'.format(arg))

    # success ... return args
    return out


###########################################################################################
# main
###########################################################################################
if __name__ == '__main__':
    args = read_args(
        'Reads issues from a github repo, creating Todoist tasks.',
    [
        'TODOIST_API_TOKEN',
        'TODOIST_PROJECT_NAME',
        'GITHUB_API_TOKEN',
        'GITHUB_REPO_NAME',
        'GITHUB_ASSIGNEE'
    ])

    # API tokens are assumed to be in environment variables if not defined on the command line
    create_todoist_tasks_from_github_issues(
        todoist_api_token=args.TODOIST_API_TOKEN, todoist_project_name=args.TODOIST_PROJECT_NAME,
        github_api_token=args.GITHUB_API_TOKEN, github_repo_name=args.GITHUB_REPO_NAME,
        github_assignee=args.GITHUB_ASSIGNEE
    )
