"""
Add Renovate support to a Drupal codebase
"""

import os
import re
import subprocess

import click
import requests

from . import util


@click.command()
@click.option(
    "--gitlab",
    help="API endpoint of the GitLab instance.",
    default="https://gitlab.axl8.xyz/api/v4/",
    show_default=True,
)
@click.option("--repo", help="Repository path, e.g. axl/site")
@click.option(
    "--gitlab-token",
    help="GitLab token to setup pipeline and environment variables.",
    default=lambda: os.environ.get("AXL_GITLAB_TOKEN"),
    prompt=True,
)
def main(repo, gitlab, gitlab_token):
    """
    Main entrypoint for init-renovate
    """
    if not os.path.exists(".gitlab-ci.yml"):
        util.write_error(
            "Can't find .gitlab-ci.yml. "
            + "Please make sure you are running this command in the correct directory."
        )
        return 1

    if not repo or not gitlab:
        try:
            gitlab, repo = get_repo_details()
        except RuntimeError:
            util.write_error(
                "Could not get repository details. "
                + "Please specify details using --repo and --gitlab options."
            )
            return 1

    os.makedirs(".gitlab", exist_ok=True)
    util.copy_package_file("files/renovate/renovate.yml", ".gitlab/renovate.yml")
    util.copy_package_file("files/renovate/renovate.json", "renovate.json")
    configjs = util.read_package_file("files/renovate/config.js")
    configjs = configjs.replace("{repo}", repo)
    configjs = configjs.replace("{gitlab}", gitlab)
    util.write_file("config.js", configjs)

    # Make GitLab requests
    gitlab_api_url = f"https://{gitlab}/api/v4"
    try:
        ensure_gitlab_token(gitlab_api_url, repo, gitlab_token)
        ensure_gitlab_pipeline(gitlab_api_url, repo, gitlab_token)
        util.write_important(
            """
        Edit your .gitlab-ci.yml file to include '.gitlab/renovate.yml'
        using include task. For example:

        include:
          - local: .gitlab/renovate.yml

        Also, make sure that no other jobs run during schedule by adding
        'except' key as follows:

        drupal_codequality:
          ...
          except:
            - schedule

        Commit the files .gitlab/renovate.yml, renovate.json, config.json,
        and .gitlab-ci.yml. Push to master to begin using Renovate.
        """
        )
    except RuntimeError:
        return 1

    return 0


def get_repo_details():
    """
    Get GitLab URL from the current git repository.
    """
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        stdout=subprocess.PIPE,
        check=False,
    )
    repo_path = result.stdout.decode("utf-8")
    git_url_match = re.match(r"^git@([^:]+):(.+)\.git$", repo_path)
    if git_url_match is None:
        git_url_match = re.match(r"^https?://([^/]+)/(.+)\.git$", repo_path)
    if git_url_match is None:
        raise RuntimeError

    return (git_url_match.group(1), git_url_match.group(2))


def ensure_gitlab_token(gitlab_api, repo, gitlab_token):
    """
    Create GITLAB_TOKEN variable *if* it doesn't already exist.
    See https://docs.gitlab.com/ee/api/project_level_variables.html
    """
    repo_url = repo.replace("/", "%2F")
    resp = requests.post(
        f"{gitlab_api}/projects/{repo_url}/variables",
        data={"key": "GITLAB_TOKEN", "value": gitlab_token},
        headers={"PRIVATE-TOKEN": gitlab_token},
    )

    if resp.status_code == 200 or resp.status_code == 201:
        util.write_info("GITLAB_TOKEN variable created")
        return

    if "error" in resp.json():
        util.write_error(f"Could not set variable. Response code: {resp.status_code}")
        util.write_error(f"Error: {resp.json()['error']}")
        raise RuntimeError

    if (
        resp.status_code == 400
        and "has already been taken" in resp.json()["message"]["key"][0]
    ):
        util.write_warning("GITLAB_TOKEN variable already exists")
        return

    util.write_error(f"Could not set variable. Response code: {resp.status_code}")
    util.write_error(resp.text)
    raise RuntimeError


def ensure_gitlab_pipeline(gitlab_api, repo, gitlab_token):
    """
    Create pipeline schedule *if* one doesn't already exist.
    https://docs.gitlab.com/ee/api/pipeline_schedules.html
    """
    repo_url = repo.replace("/", "%2F")
    resp = requests.get(
        f"{gitlab_api}/projects/{repo_url}/pipeline_schedules",
        headers={"PRIVATE-TOKEN": gitlab_token},
    )
    if resp.status_code != 200:
        util.write_error(
            f"Failed to get existing scheduled pipelines. Code: {resp.status_code}"
        )
        raise RuntimeError

    if len(resp.json()) > 0:
        util.write_warning("Scheduled pipeline already exists")
        return

    pipeline = {"description": "Run Renovate", "ref": "master", "cron": "0 */6 * * *"}
    resp = requests.post(
        f"{gitlab_api}/projects/{repo_url}/pipeline_schedules",
        data=pipeline,
        headers={"PRIVATE-TOKEN": gitlab_token},
    )

    if resp.status_code == 200 or resp.status_code == 201:
        util.write_info("Pipeline schedule created")
        return

    util.write_error(
        f"Could not create pipeline schedule. Response code: {resp.status_code}"
    )
    util.write_error(resp.text)
    raise RuntimeError()
