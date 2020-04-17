import argparse
import json
import os
import pkgutil
import shutil

from . import util


def main():
    if (not os.path.exists('composer.json')):
        print('Could not find composer.json in the current directory')
        return 2

    composer = json.loads(util.readFile('composer.json'))
    name = composer['name'].split('/')
    name = name[1] if len(name) == 2 else name[0]
    docroot = composer['extra']['drupal-scaffold']['locations']['web-root'].strip(
        '/')

    if (docroot == ''):
        print("Could not determine docroot. Make sure your composer.json is valid.")
        return 3

    cache = ''
    if ('drupal/redis' in composer['require'].keys()):
        cache = 'redis'
    elif ('drupal/memcache' in composer['require'].keys()):
        cache = 'memcached'

    generateLandoFiles(name, docroot, cache)


def generateLandoFiles(name, docroot, cache):
    services = ''
    tooling = ''
    if (cache == 'memcached'):
        services = """  cache:
    type: memcached:1
"""
    elif (cache == 'redis'):
        services = """  cache:
    type: redis:5
"""
        tooling = """  redis-cli:
    service: cache
"""

    yml = pkgutil.get_data(__name__, 'files/lando/lando.yml').decode()
    yml = yml.replace('{name}', name)
    yml = yml.replace('{docroot}', docroot)
    yml = yml.replace('{services}', services)
    yml = yml.replace('{tooling}', tooling)
    util.writeFile('.lando.yml', yml)

    if not os.path.isdir('.lando'):
        os.mkdir('.lando')
    util.copyPackageFile('files/lando/php.ini', '.lando/php.ini')

    util.copyPackageFile('files/lando/settings.lando.php',
                         docroot + '/sites/default/settings.lando.php')

    settingsFile = f'{docroot}/sites/default/settings.php'
    if (not os.path.exists(settingsFile)):
        print("Copying settings.php...")
        shutil.copyfile(
            f'{docroot}/sites/default/default.settings.php', settingsFile)

    settings = util.readFile(settingsFile)
    if (settings.find('settings.lando.php') == -1):
        settings += """
include $app_root . '/' . $site_path . '/settings.lando.php';
"""
        util.writeFile(settingsFile, settings)

    return 0
