#!/bin/sh
mymt=/var/www/minitage/django/bisonvert-maintenance
cd $mymt
source sys/share/minitage/minitage.env
bv_manage_script --script=rating_purge --settings=ecov.conf.settings_neutron
