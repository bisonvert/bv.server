# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

import os.path

##########################################################
# Variables to set first

DEBUG = False
PROJECT_ROOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')

##########################################################
# Loading default settings

try:
    path = "../settings.py"
    path = os.path.join(os.path.dirname(__file__), path)
    execfile(path)
except ImportError, e:
    import sys
    sys.stderr.write("Unable to read settings.py\n")
    sys.exit(1)

##########################################################
# Specific settings

PROJECT_ROOT_URL = 'http://www.bisonvert.net/'

# For SQL Query logger
SQL_LOG_PATHFILE = '/var/makina/bv/logs/bv2_sql.log'
SQL_LOG = False

# Path to log for cron scripts
SCRIPTS_LOG_PATH = "/var/makina/bv/logs/cron"
SCRIPTS_LOG_PREFIX = "www2-bisonvert-net"

# Google Maps
GOOGLE_MAPS_API_KEY = 'ABQIAAAAdpFW60dSCKARKFcvLnPNCBTv_nDLR0w2IaffJfImpBWh5Kpi4hTe3dARqJw_K8QlLP_2DJlyY_CzJg'

# Google Analytics
GOOGLE_ANALYTICS_KEY = 'UA-1699105-8'
GOOGLE_ANALYTICS_ENABLE = True

# Google Adsense
GOOGLE_ADSENSE_ENABLE = False

# Parameter to set to True in production: exclude my own trips in result of search
EXCLUDE_MY_TRIPS = True

# Memcache
#CACHE_BACKEND = 'memcached://127.0.0.1:11211/?timeout=1800&max_entries=600'
#CACHE_KEY = 'bv-www2'

ADMINS = (
    ('BisonVert Admins', 'admin@bisonvert.net'),
)

# for admin messages
EMAIL_SUBJECT_PREFIX = '[BisonVert-Django] '
SERVER_EMAIL = 'admin@bisonvert.net'

# Emails
FROM_EMAIL = 'contact@bisonvert.net'
CONTACT_EMAIL = 'contact@bisonvert.net'

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'bv'             # Or path to database file if using sqlite3.
DATABASE_USER = 'dbbv'             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = 'localhost'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '5434'             # Set to empty string for default. Not used with sqlite3.

EMAIL_HOST = '127.0.0.1'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False

##########################################################
# Loading common settings for production

try:
    path = "common_settings_prod.py"
    path = os.path.join(os.path.dirname(__file__), path)
    execfile(path)
except ImportError, e:
    import sys
    sys.stderr.write("Unable to read common_settings_prod.py\n")
    sys.exit(1)
