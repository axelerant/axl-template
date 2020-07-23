FROM composer:1.10 AS composer

FROM python:3.8-alpine

LABEL io.whalebrew.name init-drupal

COPY --from=composer /usr/lib/lib* /usr/lib/
COPY --from=composer /usr/local/lib/php/ /usr/local/lib/php/
COPY --from=composer /usr/local/bin/* /usr/local/bin/
COPY --from=composer /usr/local/etc/php /usr/local/etc/php
COPY --from=composer /usr/share/git-core /usr/share/git-core/
COPY --from=composer /usr/libexec/ /usr/libexec/
COPY --from=composer /usr/bin/composer /usr/bin/git* /usr/bin/ssh* /usr/bin/

RUN composer global require hirak/prestissimo

COPY . /home/axl-template/
WORKDIR /home/axl-template

RUN python setup.py install

WORKDIR /workdir
ENTRYPOINT [ "init-drupal" ]
