#!/var/www/minitage/django/bisonvert-maintenance/bin/djangopy

import os
# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "ecov.conf.settings_neutron"

# SSL proxy -> force https
#os.environ['HTTPS'] = 'on'

from django.core.servers.fastcgi import runfastcgi

runfastcgi(daemonize="false", method="threaded")

