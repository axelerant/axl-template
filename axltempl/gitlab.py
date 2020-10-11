"""
Add Gitlab support to a Drupal codebase
"""

import json
import os

from . import util
from . import drupal


def main():
    """
    Main entrypoint for init-gitlab
    """
    if not os.path.exists("composer.json"):
        util.write_error("Could not find composer.json in the current directory")
        return 2

    composer = json.loads(util.read_file("composer.json"))
    try:
        scaffold_opts = composer["extra"]["drupal-scaffold"]
        docroot = scaffold_opts["locations"]["web-root"].strip("/")
    except KeyError:
        docroot = "." if composer["name"] == "drupal/drupal" else ""

    if docroot == "":
        util.write_error(
            "Could not determine docroot. Make sure your composer.json is valid."
        )
        return 3

    generate_gitlab_files(docroot)
    return 0


def generate_gitlab_files(docroot):
    """
    Generate gitlab files in the docroot
    """

    yml = util.read_package_file("files/gitlab/gitlab-ci.yml")
    yml = yml.replace("{_docroot_}", docroot)
    util.write_file(".gitlab-ci.yml", yml)

    os.makedirs(".gitlab", mode=0o755, exist_ok=True)
    util.copy_package_file(
        "files/gitlab/settings.local.php", ".gitlab/settings.local.php"
    )
    ci_sh = util.read_package_file("files/gitlab/ci.sh")
    ci_sh = ci_sh.replace("{_docroot_}", docroot)
    util.write_file(".gitlab/ci.sh", ci_sh)
    os.chmod(".gitlab/ci.sh", 0o755)

    # Generate gitlab development override configuration.
    dir_default = f"{docroot}/sites/default"
    if not os.path.exists(dir_default):
        util.write_error(
            f'The "{dir_default}" directory is missing. '
            + "Unable to generate GitLab CI configuration files."
        )
        util.write_info(
            "This is probably due to composer installation failure. "
            + "Run init-gitlab after running composer install."
        )
        return 2

    settings_file = drupal.ensure_settings_file(docroot)
    drupal.modify_settings_file(
        settings_file,
        """if (file_exists($app_root . '/' . $site_path . '/settings.local.php')) {
  include $app_root . '/' . $site_path . '/settings.local.php';
}""",
    )

    util.write_info("Successfully created GitLab CI files.")
    util.write_important(
        "Change the database image from mariadb to your desired image in .gitlab-ci.yml."
    )

    return 0
