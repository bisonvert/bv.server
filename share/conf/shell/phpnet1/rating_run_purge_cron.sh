#!/bin/sh
mymt=/var/makina/bv/minitage/django/bisonvert
cd $mymt
source sys/share/minitage/minitage.env
bv_manage_script --script=rating_purge --settings=ecov.conf.settings_www-bisonvert-net
