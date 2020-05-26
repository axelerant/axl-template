import json
import os
import pkgutil
import shutil

import click

from . import util


@click.command()
@click.argument("name")
@click.option(
    "--directory",
    help="Directory where the files should be set up (e.g., drupal). The directory will be emptied.",
    type=click.Path(exists=False, file_okay=False),
    default="drupal",
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
@click.option("--lando", help="Add Lando support", is_flag=True)
@click.option(
    "--force",
    "-f",
    help="Force delete the target directory if it exists",
    is_flag=True,
)
def main(
    name, directory, description, core_package, docroot, no_install, cache, lando, force
):
    """
    Scaffold a Drupal site template

    Create a Drupal site template with NAME.
    Where NAME is the name of your application package (e.g., axelerant/site)
    """
    if os.path.isdir(directory):
        if not force:
            util.writeError(
                f'The "{directory}" directory already exists. Please delete it before running or use the -f option.'
            )
            return 2
        util.writeWarning(f'Removing "{directory}" directory...')
        shutil.rmtree(directory, True)

    os.mkdir(directory)
    os.chdir(directory)
    os.system('git init; git commit --allow-empty -m "Initial commit"')

    generateDrupalFiles(
        name=name,
        description=description,
        core=core_package,
        docroot=docroot,
        cacheService=cache,
    )

    if not no_install:
        if shutil.which("composer") is not None:
            status = os.system("composer install -o")
            if status != 0:
                util.writeError('Composer is unable to resolves and install the dependencies. Skipping install...')
        else:
            util.writeWarning("Cannot find composer. Skipping install...")

    if lando:
        from . import lando

        name = name.split("/")
        name = name[1] if len(name) == 2 else name[0]
        util.writeInfo("Adding Lando support...")
        lando.generateLandoFiles(name, docroot, cache)

    os.chdir("..")
    return 0


def generateDrupalFiles(
    name, description="", core="core", docroot="web", cacheService=""
):
    composer = getComposerTemplate(
        name=name,
        description=description,
        core=core,
        docroot=docroot,
        cacheService=cacheService,
    )
    composer = sortComposerPackages(composer)
    with open("composer.json", "w") as composer_file:
        json.dump(composer, composer_file, indent=4)
    util.writeFile(".gitignore", getGitignore(docroot))

    util.copyPackageFile("files/drupal/load.environment.php", "load.environment.php")
    util.copyPackageFile("files/drupal/.env.example", ".env.example")

    os.mkdir("drush")
    os.mkdir("drush/sites")
    util.copyPackageFile("files/drupal/drush.yml", "drush/drush.yml")
    util.copyPackageFile("files/drupal/self.site.yml", "drush/sites/self.site.yml")

    pass


def getComposerTemplate(name, description, core, docroot, cacheService):
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
        composer["require"]["drupal/core"] = "^8.8"
    if core == "recommended":
        composer["require"]["drupal/core-recommended"] = "^8.8"
    if cacheService == "redis":
        composer["require"]["drupal/redis"] = "^1.4"
    if cacheService == "memcache":
        composer["require"]["drupal/memcache"] = "^2.0"
    return composer


def sortComposerPackages(composer):
    composer["require"] = sortDictionaryByKeys(composer["require"])
    composer["require-dev"] = sortDictionaryByKeys(composer["require-dev"])
    return composer


def sortDictionaryByKeys(dict):
    sortedDict = {}
    for key in sorted(dict.keys()):
        sortedDict[key] = dict[key]
    return sortedDict


def getGitignore(docroot):
    gitignore = pkgutil.get_data(__name__, "files/drupal/.gitignore.template").decode()
    gitignore = gitignore.replace("{docroot}", docroot)
    return gitignore
