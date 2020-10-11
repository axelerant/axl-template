"""
Drupal codebase template main module
"""

import json
import os
import pkgutil
import shutil
import subprocess
import sys

import click

from . import click_types
from . import gitlab
from . import lando
from . import util


DEFAULT_CORE_VERSION = "^8.9.0"


@click.command()
@click.argument("name", type=click_types.COMPOSER_PACKAGE)
@click.option(
    "--directory",
    help="Directory where the files should be set up (e.g., drupal). "
    + "The directory will be emptied. The default is based on the specified name.",
    type=click.Path(exists=False, file_okay=False),
    default="",
)
@click.option("--description", help="Description of the package", default="")
@click.option(
    "--core-package",
    "-core",
    "core_package",
    help="Select the core package",
    type=click.Choice(["core", "recommended"], case_sensitive=False),
    show_default=True,
)
@click.option(
    "--core",
    "core_package",
    help="Select the drupal/core package",
    flag_value="core",
    default=True,
)
@click.option(
    "--recommended",
    "core_package",
    help="Select the drupal/core-recommended package",
    flag_value="recommended",
)
@click.option(
    "--core-version",
    help="Drupal core version",
    default=DEFAULT_CORE_VERSION,
    show_default=True,
)
@click.option(
    "--docroot", help="The document root", type=click.Path(exists=False), default="web"
)
@click.option(
    "--cache",
    help="Add a cache service",
    type=click.Choice(["redis", "memcache"], case_sensitive=False),
)
@click.option("--lando", "add_lando", help="Add Lando support", is_flag=True)
@click.option("--gitlab", "add_gitlab", help="Add GitLab support", is_flag=True)
@click.option(
    "--force",
    "-f",
    help="Force delete the target directory if it exists",
    is_flag=True,
)
def main(
    name: util.ComposerVersion,
    directory,
    description,
    core_package,
    core_version,
    docroot,
    cache,
    add_lando,
    add_gitlab,
    force,
):
    """
    Scaffold a Drupal site template

    Create a Drupal site template with NAME.
    Where NAME is the name of your application package (e.g., axelerant/site)
    """
    ensure_memory_limit()

    if directory == "":
        directory = name.get_package_name()

    prepare_base_directory(directory, force)
    os.chdir(directory)
    os.system('git init; git commit --allow-empty -m "Initial commit"')

    generate_drupal_files(
        name=name.get_name(),
        description=description,
        core=core_package,
        core_version=core_version,
        docroot=docroot,
        cache_service=cache,
    )

    run_composer_install()

    settings_file = ensure_settings_file(docroot)
    modify_settings_file(
        settings_file,
        "$settings['config_sync_directory'] = '../config/sync';",
    )

    write_settings_env(docroot)

    if add_lando:
        util.write_info("Adding Lando support...")
        lando.generate_lando_files(name.get_package_name(), docroot, cache)

    if add_gitlab:
        util.write_info("Adding GitLab support...")
        gitlab.generate_gitlab_files(docroot)

    return 0


def ensure_memory_limit():
    """
    Make sure we have enough memory for composer to work.
    """
    if shutil.which("php") is None:
        util.write_error("Cannot find php.")
        sys.exit(3)

    mem_limit = os.getenv("COMPOSER_MEMORY_LIMIT")
    if mem_limit == "-1":
        return

    php_mem_limit = subprocess.check_output(
        ["php", "-r", "echo ini_get('memory_limit');"]
    ).decode("utf-8")
    if php_mem_limit == "-1":
        return

    util.write_error(
        "Composer typically requires a lot of memory, especially with Drupal"
    )
    util.write_error(f"Current PHP value configured: {php_mem_limit}")
    util.write_error(f"Current composer value configured: {mem_limit}")
    util.write_error(
        "Consider setting the limit to -1 with either of the below methods"
    )
    util.write_error("- PHP settings - memory_limit option")
    util.write_error("- COMPOSER_MEMORY_LIMIT environment variable")
    util.write_warning(
        "Read {} for more details".format(
            "https://getcomposer.org/doc/articles/troubleshooting.md#memory-limit-errors"
        )
    )
    should_continue = click.prompt(
        "Do you want to continue anyway?", "yes", show_default=True
    )
    if should_continue == "yes":
        return
    sys.exit(3)


def prepare_base_directory(directory, force):
    """
    Create the base directory while deleting the files if forced.
    We need the directory to be empty.
    """
    if directory in ("", "."):
        directory = os.getcwd()

    if not os.path.exists(directory):
        os.mkdir(directory)
        return

    files_to_del = os.listdir(directory)
    if len(files_to_del) > 0 and not force:
        util.write_error(
            "The directory needs to be empty for this command to run. "
            + "Please delete the files or use the -f option."
        )
        sys.exit(2)

    try:
        for file in files_to_del:
            util.write_warning(f'Removing "{file}"...')
            if os.path.isdir(file):
                shutil.rmtree(file)
            else:
                os.remove(file)
    except OSError as err:
        util.write_error(f'Failed deleting files in the "{directory}" directory')
        util.write_error(str(err))
        sys.exit(2)


def run_composer_install():
    """
    Run composer install and handle errors
    """
    if shutil.which("composer") is None:
        util.write_error("Cannot find composer. Aborting...")
        sys.exit(4)

    composer_run = subprocess.run(
        "composer install --ignore-platform-reqs -o", shell=True, check=False
    )
    if composer_run.returncode != 0:
        util.write_error("Error when running 'composer install'. Aborting...")
        util.write_error("Make sure you have set an adequate PHP memory limit.")
        util.write_warning(
            "Read {} for more details".format(
                "https://getcomposer.org/doc/articles/troubleshooting.md#memory-limit-errors"
            )
        )
        sys.exit(4)


def generate_drupal_files(
    name,
    description="",
    core="core",
    core_version=DEFAULT_CORE_VERSION,
    docroot="web",
    cache_service="",
):
    """
    Generate Drupal files based on the given options
    """
    composer = get_composer_template(
        name=name,
        description=description,
        core=core,
        core_version=core_version,
        docroot=docroot,
        cache_service=cache_service,
    )
    composer = sort_composer_packages(composer)
    with open("composer.json", "w") as composer_file:
        json.dump(composer, composer_file, indent=4)
    util.write_file(".gitignore", get_gitignore(docroot))

    util.copy_package_file("files/drupal/load.environment.php", "load.environment.php")
    util.copy_package_file("files/drupal/.env.example", ".env.example")

    os.makedirs("drush/sites", mode=0o755, exist_ok=True)

    drush_yml = util.read_package_file("files/drupal/drush.yml")
    drush_yml = drush_yml.replace("{name}", name)
    util.write_file("drush/drush.yml", drush_yml)

    util.copy_package_file("files/drupal/self.site.yml", "drush/sites/self.site.yml")

    os.makedirs("config/sync", mode=0o755, exist_ok=True)
    util.write_file("config/sync/.gitkeep", "")

    os.makedirs(docroot + "/modules/custom", mode=0o755, exist_ok=True)
    util.write_file(docroot + "/modules/custom/.gitkeep", "")

    os.makedirs(docroot + "/themes/custom", mode=0o755, exist_ok=True)
    util.write_file(docroot + "/themes/custom/.gitkeep", "")

    util.copy_package_file("files/drupal/renovate.json", "renovate.json")


def get_composer_template(
    name, description, core, core_version, docroot, cache_service
):
    """
    Get the composer template from package and modify it as per given options
    """
    composer = json.loads(pkgutil.get_data(__name__, "files/drupal/composer.json"))
    composer["name"] = name
    composer["description"] = description
    composer["extra"]["drupal-scaffold"]["locations"]["web-root"] = docroot + "/"
    composer["extra"]["installer-paths"] = {
        docroot + "/core": ["type:drupal-core"],
        docroot + "/libraries/{$name}": ["type:drupal-library"],
        docroot + "/modules/contrib/{$name}": ["type:drupal-module"],
        docroot + "/profiles/contrib/{$name}": ["type:drupal-profile"],
        docroot + "/themes/contrib/{$name}": ["type:drupal-theme"],
        "drush/Commands/contrib/{$name}": ["type:drupal-drush"],
        docroot + "/modules/custom/{$name}": ["type:drupal-custom-module"],
        docroot + "/themes/custom/{$name}": ["type:drupal-custom-theme"],
    }

    if core == "core":
        composer["require"]["drupal/core"] = core_version
    if core == "recommended":
        composer["require"]["drupal/core-recommended"] = core_version
    if cache_service == "redis":
        composer["require"]["drupal/redis"] = "^1.4"
    if cache_service == "memcache":
        composer["require"]["drupal/memcache"] = "^2.0"
    composer["require"]["drupal/core-composer-scaffold"] = core_version
    return composer


def sort_composer_packages(composer):
    """
    Sort the packages in a composer array
    """
    composer["require"] = sort_dictionary_by_keys(composer["require"])
    composer["require-dev"] = sort_dictionary_by_keys(composer["require-dev"])
    return composer


def sort_dictionary_by_keys(input_dict):
    """
    Sort the dictionary by keys in alphabetical order
    """
    sorted_dict = {}
    for key in sorted(input_dict.keys()):
        sorted_dict[key] = input_dict[key]
    return sorted_dict


def get_gitignore(docroot):
    """
    Get gitignore template from the package
    """
    gitignore = pkgutil.get_data(__name__, "files/drupal/.gitignore.template").decode()
    gitignore = gitignore.replace("{docroot}", docroot)
    return gitignore


def ensure_settings_file(docroot):
    """
    Make sure the settings.php file exists
    """
    settings_path = f"{docroot}/sites/default"
    settings_file = f"{settings_path}/settings.php"
    if not os.path.exists(settings_path):
        os.makedirs(settings_path, exist_ok=True)

    settings_source = f"{docroot}/sites/default/default.settings.php"
    if not os.path.exists(settings_source):
        return False

    if not os.path.exists(settings_file):
        util.write_info("Copying settings.php...")
        shutil.copyfile(settings_source, settings_file)
    return settings_file


def write_settings_env(docroot):
    """
    Write settings.env.php file in correct location
    """
    settings_file = ensure_settings_file(docroot)
    util.copy_package_file(
        "files/drupal/settings.env.php", docroot + "/sites/default/settings.env.php"
    )
    modify_settings_file(
        settings_file, "include $app_root . '/' . $site_path . '/settings.env.php';"
    )


def modify_settings_file(settings_file, line):
    """
    Add a line to the settings.php file if present, else show a warning
    """
    if settings_file and os.path.exists(settings_file):
        settings = util.read_file(settings_file)
        if settings.find(line) == -1:
            settings += "\n" + line + "\n"
            util.write_file(settings_file, settings)
    else:
        util.write_warning(
            "Could not write to settings.php. Remember to add this line after installation."
        )
        util.write_warning(line)
