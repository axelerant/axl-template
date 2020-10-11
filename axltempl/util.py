"""
Utility functions
"""

import pkgutil
import click


def read_file(file):
    """
    Read entire file contents
    """
    with open(file, "r") as fobj:
        return fobj.read()
    return ""


def read_package_file(file):
    """
    Read entire contents of a package file
    """
    return pkgutil.get_data(__name__, file).decode()


def write_file(file, contents):
    """
    Write contents to a file
    """
    with open(file, "w") as fobj:
        fobj.write(contents)


def copy_package_file(src_file, dest_file):
    """
    Copy package file to dest_file
    """
    write_file(dest_file, pkgutil.get_data(__name__, src_file).decode())


def write_error(line):
    """
    Write a single error line using click
    """
    click.secho(line, fg="red", err=True)


def write_warning(line):
    """
    Write a single warning line using click
    """
    click.secho(line, fg="yellow")


def write_info(line):
    """
    Write a single info line using click
    """
    click.secho(line, fg="green")


def write_important(line, prefix="[IMPORTANT] "):
    """
    Write a single info line with important prefix
    """
    click.secho(prefix + line, fg="green", bold=True)


def sort_dictionary_by_keys(input_dict):
    """
    Sort the dictionary by keys in alphabetical order
    """
    sorted_dict = {}
    for key in sorted(input_dict.keys()):
        sorted_dict[key] = input_dict[key]
    return sorted_dict
