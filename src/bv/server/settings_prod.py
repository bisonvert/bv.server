# -*- coding: utf-8 -*-
"""Default settings for Bisonvert Serverside application.

Please, do not make your modifications here, but on a specific local_settings.py
file at the root of the project.
"""

# you can search for parameters to override inside this module.
from bv.server.settings import *

# from local_settings.py
# LOCAL_SETTINGS_DEFINED = True
DEFAULT_CLIENT_ROOT_URL = 'http://88.191.227.98:8095'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'



# Database
DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'bvserver'
DATABASE_USER = 'bv_user'
DATABASE_PASSWORD = 'secret'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5434'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# For SQL Query logger - DEFAULT
SQL_LOG_PATHFILE = os.path.join(PROJECT_ROOT_PATH, 'log')
SQL_LOG = False

# Path to log for cron scripts - DEFAULT
SCRIPTS_LOG_PATH = os.path.join(PROJECT_ROOT_PATH, 'cron')
SCRIPTS_LOG_PREFIX = "instancename"

# Google Maps - DEFAULT
GOOGLE_MAPS_API_KEY = 'ABQIAAAAy87PVt3dY6PzmE8_gGTptxThaDuXe-OGoRqQhRYx2Y7yrxbpQxRK8dOBLyA4n7oVxl182B2EoXCTew'

# Google Analytics - DEFAULT
GOOGLE_ANALYTICS_KEY = ''
GOOGLE_ANALYTICS_ENABLE = False

# Google Adsense - DEFAULT
GOOGLE_ADSENSE_KEY = ''
GOOGLE_ADSENSE_SLOT = ''
GOOGLE_ADSENSE_WIDTH = ''
GOOGLE_ADSENSE_HEIGHT = ''
GOOGLE_ADSENSE_ENABLE = False


# Parameter to set to True in production: exclude my own trips in result of search - DEFAULT
EXCLUDE_MY_TRIPS = False

# JS extension
JS_EXT = '-min.js' if not DEBUG else '.js'

# Memcache - DEFAULT
#CACHE_BACKEND = 'memcached://127.0.0.1:11211/?timeout=1800&max_entries=300'
#CACHE_KEY = 'bv'

ADMINS = ()
MANAGERS = ADMINS

# for admin messages - DEFAULT
EMAIL_SUBJECT_PREFIX = '[Django] '
SERVER_EMAIL = 'admin@foo.bar'

# Emails - DEFAULT
FROM_EMAIL = 'admin@foo.bar'
CONTACT_EMAIL = 'admin@foo.bar'


# DEFAULT
EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
 
# Session configuration
SESSION_COOKIE_AGE            = 7200 # 2 hours
SESSION_PERSISTENT_COOKIE_AGE = 31536000 # 1 year 
