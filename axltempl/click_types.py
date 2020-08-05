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

        return list(map(ComposerPackage.parse_package, packages))

    @staticmethod
    def parse_package(value):
        """
        Parse a composer package version string into a ComposerVersion type
        """
        try:
            composer_version = util.ComposerVersion.from_package_string(value)
        except ValueError as err:
            raise BadParameter(err)
        return composer_version


COMPOSER_PACKAGE = ComposerPackage()
