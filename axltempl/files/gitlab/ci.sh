#!/usr/bin/env bash

dir=$(dirname $0)
docroot={_docroot_}

set -ex

cp ${dir}/settings.local.php ${dir}/../${docroot}/sites/default/settings.local.php

sed -ri -e "s!/var/www/html/${docroot}!$CI_PROJECT_DIR/${docroot}!g" /etc/apache2/sites-available/*.conf
sed -ri -e "s!/var/www/html/${docroot}!$CI_PROJECT_DIR/${docroot}!g" /etc/apache2/apache2.conf /etc/apache2/conf-available/*.conf

service apache2 start
