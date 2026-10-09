FROM php:8.4-fpm

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev \
    && docker-php-ext-install pdo_pgsql \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /var/www/html


# Syntax
#
# apt = Debian package manager APT=Advanced Package Tool
# -y = --yes = automatically answer yes to all questions
# --no-install-recommends = not to install recommended
# libpq-dev:
#   lib = library
#   pq = name of client's C-library PostgreSQL
#   dev = development 
# needed for extension pdo_pgsql, cuz it's not being dowloaded itself, but compiles
# 
# docker-php-ext-install = extension script for pdo_psql extension
# rm -rf = clearing the cache

# WORKDIR = working directory where commands will be executed in the future
# /var/www/html = default dorectory for web files in Linux
