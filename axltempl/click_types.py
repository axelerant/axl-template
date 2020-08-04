"""
Click parameter types
"""

import shlex

import click
from click.exceptions import BadParameter

from . import util


class ComposerPackage(click.ParamType):
    """
    Composer package type for click
    """

    name = "composer_package"

    def convert(self, value, param, ctx):
        packages = shlex.split(value)

        return map(ComposerPackage.parse_package, packages)

    @staticmethod
    def parse_package(value):
        """
        Parse a composer package version string into a ComposerVersion type
        """
        if ":" in value:
            name, version = value.split(":")
        else:
            name = value
            version = ""

        parts = name.split("/")
        if len(parts) == 1:
            name = "drupal/" + name
        elif len(parts) != 2:
            raise BadParameter(f"{value} is not a valid composer package name")
        return util.ComposerVersion(name, version)


COMPOSER_PACKAGE = ComposerPackage()
