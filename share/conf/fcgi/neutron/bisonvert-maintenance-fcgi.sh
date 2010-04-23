#!/bin/sh

source /var/www/minitage/django/bisonvert-maintenance/sys/share/minitage/minitage.env

exec /var/www/minitage/django/bisonvert-maintenance/bin/djangopy /var/www/minitage/django/bisonvert-maintenance/src/bisonvert/src/share/conf/fcgi/neutron/bisonvert-maintenance-fcgi.py $*

