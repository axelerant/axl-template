import os
import pkgutil
import shutil


def readFile(file):
    with open(file, 'r') as f:
        return f.read()
    return ''


def writeFile(file, contents):
    with open(file, 'w') as f:
        f.write(contents)


def copyPackageFile(srcFile, destFile):
    writeFile(destFile, pkgutil.get_data(__name__, srcFile).decode())
