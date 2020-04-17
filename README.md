# Template scripts

## init-drupal

(*Requires Python 3.6+*)

Scaffold a Drupal codebase in a subdirectory.

### Usage for init-drupal

```bash
usage: init-drupal [-h] [--directory DIRECTORY] [--description DESCRIPTION]
                   [--core-package {core,recommended}] [--docroot DOCROOT]
                   [--force] [--no-install] [--cache CACHE] [--lando]
                   name

Scaffold a Drupal site template

positional arguments:
  name                  Name of your application package (e.g.,
                        axelerant/site)

optional arguments:
  -h, --help            show this help message and exit
  --directory DIRECTORY, -d DIRECTORY
                        Directory where the files should be set up (e.g.,
                        drupal). The directory will be emptied.
  --description DESCRIPTION, -D DESCRIPTION
                        Description of the package
  --core-package {core,recommended}, -c {core,recommended}
                        Select the core package
  --docroot DOCROOT, -r DOCROOT
                        The document root
  --force, -f           Force delete the "drupal" directory if it exists
  --no-install          Do not run composer install
  --cache CACHE         Add a cache service (either redis or memcache)
  --lando               Add Lando support
```

### Example

```bash
init-drupal axelerant/site --cache redis --c core
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
