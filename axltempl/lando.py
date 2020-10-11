"""
Add Lando support to a Drupal codebase
"""

import json
import os

from . import util
from . import drupal


def main():
    """
    Main entrypoint for init-lando
    """
    if not os.path.exists("composer.json"):
        util.write_error("Could not find composer.json in the current directory")
        return 2

    composer = json.loads(util.read_file("composer.json"))
    name = composer["name"].split("/")
    name = name[1] if len(name) == 2 else name[0]
    try:
        scaffold_opts = composer["extra"]["drupal-scaffold"]
        docroot = scaffold_opts["locations"]["web-root"].strip("/")
    except KeyError:
        docroot = "." if composer["name"] == "drupal/drupal" else ""

    if docroot == "":
        util.write_error(
            "Could not determine docroot. Make sure your composer.json is valid."
        )
        return 3

    cache = ""
    if "drupal/redis" in composer["require"].keys():
        cache = "redis"
    elif "drupal/memcache" in composer["require"].keys():
        cache = "memcached"

    generate_lando_files(name, docroot, cache)
    return 0


def generate_lando_files(name, docroot, cache):
    """
    Generate Lando files in the docroot
    """
    services = ""
    tooling = ""
    if cache == "redis":
        services = """  cache:
    app_mount: disabled
    type: redis:5
"""
        tooling = """  redis-cli:
    service: cache
"""
    elif cache == "memcached":
        services = """  cache:
    app_mount: disabled
    type: memcached:1
"""

    yml = util.read_package_file("files/lando/lando.yml")
    yml = yml.replace("{name}", name)
    yml = yml.replace("{docroot}", docroot)
    yml = yml.replace("{services}", services)
    yml = yml.replace("{tooling}", tooling)
    util.write_file(".lando.yml", yml)

    os.makedirs(".lando", mode=0o755, exist_ok=True)
    util.copy_package_file("files/lando/php.ini", ".lando/php.ini")

    # Generate lando development override configuration.
    dir_default = f"{docroot}/sites/default"
    if not os.path.exists(dir_default):
        util.write_error(
            f'The "{dir_default}" directory is missing. '
            + "Unable to generate lando override configuration files."
        )
        util.write_info(
            "This is probably due to composer installation failure. "
            + "Run init-lando after running composer install."
        )
        return 2

    lando_settings = util.read_package_file("files/lando/settings.lando.php")
    if cache == "redis":
        lando_settings += util.read_package_file("files/lando/lando.redis.php")
    elif cache == "memcached":
        lando_settings += util.read_package_file("files/lando/lando.memcache.php")
    util.write_file(docroot + "/sites/default/settings.lando.php", lando_settings)

    settings_file = drupal.ensure_settings_file(docroot)
    drupal.modify_settings_file(
        settings_file, "include $app_root . '/' . $site_path . '/settings.lando.php';"
    )

    util.write_info("Successfully created Lando configuration files.")
    util.write_important(
        "Change the database image from mariadb to your desired image in .lando.yml."
    )

    return 0
