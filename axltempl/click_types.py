"""
Click parameter types
"""

import shlex

import click
from click.exceptions import BadParameter

from . import composer


class ComposerPackages(click.ParamType):
    """
    Click type to represent a list of composer packages
    """

    name = "composer_packages"

    def convert(self, value, param, ctx):
        packages = shlex.split(value)

        return list(map(ComposerPackage.parse_package, packages))


class ComposerPackage(click.ParamType):
    """
    Click type to represent a single composer package
    """

    name = "composer_package"

    def convert(self, value, param, ctx):
        return ComposerPackage.parse_package(value)

    @staticmethod
    def parse_package(value):
        """
        Parse a composer package version string into a ComposerVersion type
        """
        try:
            composer_version = composer.ComposerVersion.from_package_string(value)
        except ValueError as err:
            raise BadParameter from err
        return composer_version


COMPOSER_PACKAGES = ComposerPackages()
COMPOSER_PACKAGE = ComposerPackage()
