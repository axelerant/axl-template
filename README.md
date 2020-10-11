# Template scripts

A set of scaffolding tools for use at Axelerant. Currently it supports:

- [Drupal](#init-drupal)
- [Lando](#init-lando)
- [GitLab](#init-gitlab)

## Requirements

You need Python 3.6+ and pip to install and use this script. Follow [these instructions](https://pip.pypa.io/en/stable/installing/) to install pip if you don't already have it.

The script relies on certain developer tools to be available when running.

- git - To initialise the project as a repository.
- composer - To download the dependencies. If composer is not present, the dependencies don't get downloaded.

Alternatively, you can use Docker to run this command. See the section below on usage with Docker for more information.

## Installation

Install this script via `pip` (or `pip3`). You can use the command to upgrade the command as well.

```bash
pip3 install --upgrade axl-template
```

## Usage with Docker _(alternate)_

Docker support is experimental right now and may throw errors. If you face issues with Docker support, please report an issue. To run `init-drupal` with Docker, run this command (for bash):

```bash
docker run -v $(pwd):/workdir axelerant/template:latest <init-drupal options>
```

The `ENTRYPOINT` is set to `init-drupal` and you can override it if you want to run other commands.

```bash
docker run -v $(pwd):/workdir -e init-lando axelerant/template:latest <init-lando options>
```

You can set aliases so that you don't have to type these commands every time.

```bash
alias init-drupal='docker run -v $(pwd):/workdir axelerant/template'
alias init-lando='docker run -v $(pwd):/workdir -e init-lando axelerant/template'
```

### Usage with whalebrew

The Docker image works with [whalebrew](https://github.com/whalebrew/whalebrew). You can install the Docker image using the following:

```bash
whalebrew install axelerant/template
```

You can then use the command `init-drupal` as normal. Whalebrew takes care of the Docker syntax for you.

### Updating with Docker

Docker images are tagged along with each tagged version. The `latest` Docker tag will point to the latest tagged release. You can update the Docker image on your machine similar to any other Docker machine.

```bash
docker pull axelerant/template
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
                                  emptied.  [default: .]

  --description TEXT              Description of the package
  -core, --core-package [core|recommended]
                                  Select the core package
  --core                          Select the drupal/core package
  --recommended                   Select the drupal/core-recommended package
  --core-version TEXT             Drupal core version  [default: ^8.9.0]
  --docroot PATH                  The document root
  --cache [redis|memcache]        Add a cache service
  --lando                         Add Lando support
  --gitlab                        Add GitLab support
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

Lando support can also be added when running `init-drupal` by passing the `--lando` option.

## init-gitlab

(*Requires Python 3.6+*)

Scaffold GitLab configuration for a Drupal site in the current directory.

### Usage for init-gitlab

```bash
usage: init-gitlab
```

No options are required. The tool reads the composer.json file and sets up the GitLab CI configuration accordingly. It also enables loading `settings.local.php` from `settings.php` so that Drupal can use proper database configuration during a CI run.

These files are created by `init-gitlab` in the `.gitlab` directory and copied by a shell script (`ci.sh`). The `.gitlab-ci.yml` file is created in the project root directly.

GitLab support can also be added when running `init-drupal` by passing the `--gitlab` option.
