import click
import pkgutil


def readFile(file):
    with open(file, "r") as f:
        return f.read()
    return ""


def readPackageFile(file):
    return pkgutil.get_data(__name__, file).decode()


def writeFile(file, contents):
    with open(file, "w") as f:
        f.write(contents)


def copyPackageFile(srcFile, destFile):
    writeFile(destFile, pkgutil.get_data(__name__, srcFile).decode())


def writeError(line):
    click.secho(line, fg="red", err=True)


def writeWarning(line):
    click.secho(line, fg="yellow")


def writeInfo(line):
    click.secho(line, fg="green")
