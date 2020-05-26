# Template scripts

## Requirements

You need Python 3.6+ and pip to install and use this script. Follow [these instructions](https://pip.pypa.io/en/stable/installing/) to install pip if you don't already have it.

The script relies on certain developer tools to be available when running.

* git - To initialise the project as a repository.
* composer - To download the dependencies. If composer is not present, the dependencies don't get downloaded.

## Installation

Install this script via `pip` (or `pip3`).

```bash
pip3 install axl-template
```

## init-drupal

(*Requires Python 3.6+*)

Scaffold a Drupal codebase in a subdirectory.

### Usage for init-drupal

```bash
Usage: init-drupal [OPTIONS] NAME

  Scaffold a Drupal site template

  Create a Drupal site template with NAME. Where NAME is the name of your
  application package (e.g., axelerant/site)

Options:
  --directory DIRECTORY           Directory where the files should be set up
                                  (e.g., drupal). The directory will be
                                  emptied.  [default: drupal]

  --description TEXT              Description of the package
  -core, --core-package [core|recommended]
                                  Select the core package
  --core                          Select the drupal/core package
  --recommended                   Select the drupal/core-recommended package
  --core-version TEXT             Drupal core version  [default: ^8.8.0]
  --docroot PATH                  The document root
  --no-install                    Do not run composer install
  --cache [redis|memcache]        Add a cache service
  --lando                         Add Lando support
  -f, --force                     Force delete the target directory if it
                                  exists

  --help                          Show this message and exit.
```

### Example

```bash
init-drupal axelerant/site --cache redis --core
```

The above command will generate a composer.json and in a `drupal` directory and run `composer install`. It will use the regular `drupal/core` package along with the Redis module and few other packages.

## init-lando

(*Requires Python 3.6+*)

Scaffold Lando configuration for a Drupal site in the current directory.

### Usage for init-lando

```bash
usage: init-lando
```

No options are required. The tool reads the composer.json file and sets up the Lando configuration accordingly. It also sets up a `settings.lando.php` file to include Lando specific database and caching configuration.

Lando support can also be added when running `init-drupal` by passing the `--lando` argument.
