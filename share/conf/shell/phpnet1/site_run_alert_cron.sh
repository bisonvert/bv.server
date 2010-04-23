#!/bin/sh
mymt=/var/makina/bv/minitage/django/bisonvert
cd $mymt
source sys/share/minitage/minitage.env
bv_manage_script --script=site_alert --settings=ecov.conf.settings_www-bisonvert-net
