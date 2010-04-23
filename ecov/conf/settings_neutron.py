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

PROJECT_ROOT_URL = 'http://bisonvert.makina-paris.net/'

# For SQL Query logger
SQL_LOG_PATHFILE = '/home/users/lgu/logs/ecov_sql.log'
SQL_LOG = False

# Path to log for cron scripts
SCRIPTS_LOG_PATH = "/var/www/bv/logs/cron"
SCRIPTS_LOG_PREFIX = "neutron"

# Google Maps
GOOGLE_MAPS_API_KEY = 'ABQIAAAAs4uFta9HYUJxCM2p-ox7zxRFfwtQYfKu1dJMt3ftivPZcIQcKBQGBFBRk56Kpy7MDmY8BVhQVDKVcQ'

# Memcache
#CACHE_BACKEND = 'memcached://127.0.0.1:11211/?timeout=1800&max_entries=300'
#CACHE_KEY = 'bv-xenecov'

ADMINS = (
    ('LGU', 'lgu@makina-corpus.com'),
    ('SBE', 'sbe@makina-corpus.com'),
)

# for admin messages
EMAIL_SUBJECT_PREFIX = '[Django BV neutron] '
SERVER_EMAIL = 'lgu@makina-corpus.com'

# Emails
FROM_EMAIL = 'makina-ecov@makina-corpus.com'
CONTACT_EMAIL = 'lgu@makina-corpus.com'

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'bv'             # Or path to database file if using sqlite3.
DATABASE_USER = 'minitage'             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = 'localhost'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '5435'             # Set to empty string for default. Not used with sqlite3.

EMAIL_HOST = '127.0.0.1'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False

#MIDDLEWARE_CLASSES += (
#    'ecov.utils.middleware.ProxyHeadersRemoveMiddleware',
#)
