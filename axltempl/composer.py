"""
Composer support functions
"""

import json
import pkgutil
import shutil
import subprocess
import sys

from . import util


def is_present():
    """
    Check if composer is present
    """
    return shutil.which("composer") is not None


def get_version():
    """
    Attempt to get composer version
    """
    if not is_present():
        raise RuntimeError("Composer not installed")

    composer_run = subprocess.run(
        "composer --version", shell=True, check=False, capture_output=True
    )

    if not composer_run.stdout.startswith(b"Composer version "):
        raise RuntimeError("Unexpected output from composer --version")

    version_string = composer_run.stdout
    end_index = version_string.find(b" ", 17)
    version = version_string[17:end_index]

    return version.decode("utf-8")


def is_version_2():
    """
    Check if we have composer 2 installed
    """
    version = get_version()
    return version[0] == "2"


def run_install():
    """
    Run composer install and handle errors
    """
    if not is_present():
        util.write_error("Cannot find composer. Aborting...")
        sys.exit(4)

    composer_run = subprocess.run(
        "composer install --no-interaction --ignore-platform-reqs -o",
        shell=True,
        check=False,
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


def require_packages(packages, dev=False):
    """
    Run composer require or require --dev
    """
    if not is_present():
        util.write_error("Cannot find composer. Aborting...")
        sys.exit(4)

    if len(packages) == 0:
        return

    cmd = "composer require "
    if dev:
        cmd += "--dev "
    cmd += " ".join([str(p) for p in packages])

    composer_run = subprocess.run(cmd, shell=True, check=False)
    if composer_run.returncode != 0:
        util.write_error("Error when running 'composer require'. Aborting...")
        util.write_error("Make sure you have set an adequate PHP memory limit.")
        util.write_warning(
            "Read {} for more details".format(
                "https://getcomposer.org/doc/articles/troubleshooting.md#memory-limit-errors"
            )
        )
        sys.exit(4)


def get_drupal_template(name, description, core, core_version, docroot, cache_service):
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

    if not is_version_2():
        composer["require"]["zaporylie/composer-drupal-optimizations"] = "^1.1"

    return composer


def sort_packages(composer):
    """
    Sort the packages in a composer array
    """
    composer["require"] = util.sort_dictionary_by_keys(composer["require"])
    composer["require-dev"] = util.sort_dictionary_by_keys(composer["require-dev"])
    return composer


class ComposerVersion:
    """
    Utility class to represent a composer package version
    """

    def __init__(self, name, version=""):
        parts = name.split("/")
        if len(parts) != 2:
            raise ValueError(f"{name} is not a valid composer package name")
        self.name = name
        self.package_vendor = parts[0]
        self.package_name = parts[1]

        if " " in version and not ("'" in version or '"' in version):
            version = f'"{version}"'
        self.version = version

    @staticmethod
    def from_package_string(package_string):
        """
        Parse a composer package version string into a ComposerVersion type
        """
        if ":" in package_string:
            name, version = package_string.split(":")
        else:
            name = package_string
            version = ""

        parts = name.split("/")
        if len(parts) == 1:
            name = "drupal/" + name
        elif len(parts) != 2:
            raise ValueError(f"{package_string} is not a valid composer package name")
        return ComposerVersion(name, version)

    def get_name(self):
        """
        Get the name of the composer package
        """
        return self.name

    def get_package_vendor(self):
        """
        Get the name of the package vendor, e.g., "drupal" in "drupal/module"
        """
        return self.package_vendor

    def get_package_name(self):
        """
        Get the name of the package name, e.g., "module" in "drupal/module"
        """
        return self.package_name

    def get_version(self):
        """
        Get the version of the composer package (if any)
        """
        return self.version

    def __str__(self) -> str:
        """
        Get string representation of the composer string
        """
        package_str = self.name
        if self.version:
            package_str += f':"{self.version}"'
        return package_str

    def __repr__(self) -> str:
        """
        Get string representation of the composer string
        """
        return self.__str__()
