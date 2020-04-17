# Template scripts

## init-drupal

*Requires Python 3.*

### Usage

```bash
usage: init-drupal [-h] [--directory DIRECTORY] [--description DESCRIPTION]
                   [--core-package {core,recommended}] [--docroot DOCROOT]
                   [--force] [--no-install] [--cache CACHE]
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
  ```

### Example

```bash
init-drupal axelerant/site --cache redis --c core
```

The above command will generate a composer.json and in a `drupal` directory and run `composer install`. It will use the regular `drupal/core` package along with the Redis module and few other packages.
