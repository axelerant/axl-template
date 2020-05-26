"""
Drupal codebase template main module
"""

import json
import os
import pkgutil
import shutil

import click

from . import lando
from . import util


DEFAULT_CORE_VERSION = "^8.8.0"


@click.command()
@click.argument("name")
@click.option(
    "--directory",
    help="Directory where the files should be set up (e.g., drupal). "
    + "The directory will be emptied.",
    type=click.Path(exists=False, file_okay=False),
    default="drupal",
    show_default=True,
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
    "--no-install", help="Do not run composer install", is_flag=True, default=False
)
@click.option(
    "--cache",
    help="Add a cache service",
    type=click.Choice(["redis", "memcache"], case_sensitive=False),
)
@click.option("--lando", "add_lando", help="Add Lando support", is_flag=True)
@click.option(
    "--force",
    "-f",
    help="Force delete the target directory if it exists",
    is_flag=True,
)
def main(
    name,
    directory,
    description,
    core_package,
    core_version,
    docroot,
    no_install,
    cache,
    add_lando,
    force,
):
    """
    Scaffold a Drupal site template

    Create a Drupal site template with NAME.
    Where NAME is the name of your application package (e.g., axelerant/site)
    """
    if os.path.isdir(directory):
        if not force:
            util.write_error(
                f'The "{directory}" directory already exists.'
                + "Please delete it before running or use the -f option."
            )
            return 2
        util.write_warning(f'Removing "{directory}" directory...')
        shutil.rmtree(directory, True)

    os.mkdir(directory)
    os.chdir(directory)
    os.system('git init; git commit --allow-empty -m "Initial commit"')

    generate_drupal_files(
        name=name,
        description=description,
        core=core_package,
        core_version=core_version,
        docroot=docroot,
        cache_service=cache,
    )

    if not no_install:
        run_composer_install()
    else:
        util.write_info("Remember to run 'composer install' manually.")

    if add_lando:
        name = name.split("/")
        name = name[1] if len(name) == 2 else name[0]
        util.write_info("Adding Lando support...")
        lando.generate_lando_files(name, docroot, cache)

    os.chdir("..")
    return 0


def run_composer_install():
    """
    Run composer install and handle errors
    """
    if shutil.which("composer") is None:
        util.write_warning("Cannot find composer. Skipping install...")
        return

    if os.system("composer install -o") != 0:
        util.write_error("Error when running 'composer install'. Skipping install...")


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

    os.mkdir("drush")
    os.mkdir("drush/sites")
    util.copy_package_file("files/drupal/drush.yml", "drush/drush.yml")
    util.copy_package_file("files/drupal/self.site.yml", "drush/sites/self.site.yml")


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
