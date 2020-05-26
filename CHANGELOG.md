
0.2.0 / 2020-05-26
==================

* Fixed "init-lando" FileNotFoundError (#6)
* Add requirements.txt
* Add default pylintrc generated using 'pylint --generate-rcfile'
* Better handle webroot detection for drupal/drupal
* Allow specifying Drupal core version
* Remind to run composer install if installation is skipped.
* Refactor composer install method
* Added check to exit if composer fails to install vendors. (#5)
* Convert print calls to click's utilities
* Update README with new options documentation
* Refactor argument parsing using click
* fix markdown lint issues

0.1.5 / 2020-04-21
==================

* Add drupal-quality-checker to drupal-scaffold.allowed-packages
* Add requirements to README.
* Handle failures when composer is not present
* Add axelerant specific dev-dependencies to the template
* Format files using black
* Install correct composer packages and bump versions.
* Add required parameter for lando to work
* Override the database image for lando
* Fix issue with generated name for lando.yml
* Fix issue with default value for lando argument
* Refactor settings.lando.php generation and add memcache support
* Add installation instructions to the readme
* Update documentation and minor tweaks
* Ensure dist directory is empty before building
* Add Lando support and script
* Refactor common tasks into an util module
* Create the directory as a git repository
* Restructure the module for clarity
* Add a simple build script
