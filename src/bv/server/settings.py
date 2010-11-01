# -*- coding: utf-8 -*-
"""Default settings for Bisonvert Serverside application.

Please, do not make your modifications here, but on a specific local_settings.py
file at the root of the project.
"""

import os.path
import datetime

# ROOT_PATH : where the source are (<..>/bv.server/src/bv/server/)
# MT_PTH    : where the whole root project is (<..>/bv.server/)
PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_MT_PATH = os.path.normpath(os.path.join(PROJECT_ROOT_PATH, *('../../..'.split('/'))))

PROJECT_ROOT_URL = 'http://api.bisonvert.net'
PROJECT_NAME = 'BisonVert'
PROJECT_NAME_URL = 'BisonVert.net'

# Database
# See dev.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# For SQL Query logger - DEFAULT
SQL_LOG_PATHFILE = '/path/to/logs/pgsql'
SQL_LOG = False

# Path to log for cron scripts - DEFAULT
SCRIPTS_LOG_PATH = "/path/to/logs/cron"
SCRIPTS_LOG_PREFIX = "instancename"

# Google Maps - DEFAULT
GOOGLE_MAPS_API_KEY = 'GoogleMapsKeyForURLUsed'

# Default map center
DEFAULT_MAP_CENTER_NAME = "France"
DEFAULT_MAP_CENTER_POINT = "POINT( 2.213749 46.227638 )"
DEFAULT_MAP_CENTER_ZOOM = 5

# Google Analytics - DEFAULT
GOOGLE_ANALYTICS_KEY = ''
GOOGLE_ANALYTICS_ENABLE = False

# Google Adsense - DEFAULT
GOOGLE_ADSENSE_KEY = ''
GOOGLE_ADSENSE_SLOT = ''
GOOGLE_ADSENSE_WIDTH = ''
GOOGLE_ADSENSE_HEIGHT = ''
GOOGLE_ADSENSE_ENABLE = False

# Mapnik
MAPNIK_CONFIGFILE = os.path.join(PROJECT_ROOT_PATH, 'ogcserver/ogcserver.conf')

# Parameter to set to True in production: exclude my own trips in result of search - DEFAULT
EXCLUDE_MY_TRIPS = True

# JS extension
JS_EXT = '-min.js' if not DEBUG else '.js'

# Memcache - DEFAULT
#CACHE_BACKEND = 'memcached://127.0.0.1:11211/?timeout=1800&max_entries=300'
#CACHE_KEY = 'bv'

# User profile
#AUTH_PROFILE_MODULE = 'accounts.userprofile'
LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/account/'
AUTH_PROFILE_MODULE = 'accounts.UserProfile'

# Custom Auth Backend : username case insensitive
AUTHENTICATION_BACKENDS = (
    'bv.server.auth.backends.ModelBackend',
)


ADMINS = ()
MANAGERS = ADMINS

# for admin messages - DEFAULT
# EMAIL_SUBJECT_PREFIX = '[Django] '
# SERVER_EMAIL = 'admin@foo.bar'

# Emails - DEFAULT
# FROM_EMAIL = 'admin@foo.bar'
# CONTACT_EMAIL = 'admin@foo.bar'

# DEFAULT
# EMAIL_HOST = 'localhost'
# EMAIL_HOST_PASSWORD = ''
# EMAIL_HOST_USER = ''
# EMAIL_PORT = 1025
# EMAIL_USE_TLS = False


# TESTING 
TEST_RUNNER = 'django.contrib.gis.tests.run_tests'
POSTGIS_TEMPLATE = 'template_postgis'
POSTGIS_SQL_PATH = '/usr/local/share'
TEST_SQL_PATH = os.path.join(PROJECT_MT_PATH, '../share/data')
TEST_SQL_FILES = ('procedures.sql', 'trigger.sql', 'additional_columns.sql')

 
# Session configuration
SESSION_COOKIE_AGE            = 7200 # 2 hours
SESSION_PERSISTENT_COOKIE_AGE = 31536000 # 1 year 
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_SECURE = None
PERSISTENT_SESSION_KEY = 'sessionpersistent'

# i18n / l10n
ugettext = lambda s: s
TIME_ZONE = 'Europe/Paris'
DEFAULT_CHARSET = 'utf-8'
SITE_ID = 1
LANGUAGE_CODE = 'fr'
LANGUAGES = (
  ('fr', ugettext('French')),
  ('en', ugettext('English')),
)

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT_PATH, 'templates'),
    os.path.join(PROJECT_ROOT_PATH, 'media/locale'),
    # os.path.join(PROJECT_ROOT_PATH, '../ecov/locale'),
)

USE_I18N = True
MEDIA_ROOT = os.path.join(PROJECT_ROOT_PATH, 'media/default/') # DEFAULT
MEDIA_URL = '/media/' # DEFAULT

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '0564bn+ryi&3xj8=se&sl!z+baoc5#0+j0erv*)eu^%r0zn59)'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'bv.server.utils.middleware.EcovSessionMiddleware',
    'bv.server.utils.middleware.QueryLoggerMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
#    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'
)

INTERNAL_IPS = ('127.0.0.1',)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'bv.server.utils.context_processors.js_ext',
    'bv.server.utils.context_processors.project_info',
    'bv.server.utils.context_processors.get_google_analytics_info',
    'bv.server.utils.context_processors.get_google_adsense_info',
    'bv.server.utils.context_processors.client_urls',
)

ROOT_URLCONF = 'bv.server.urls'
TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT_PATH, 'templates'),
    # contains mails templates
    os.path.join(PROJECT_ROOT_PATH, 'apiconsumers', 'templates'),
)

INSTALLED_APPS = (
    # django needed applications
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.gis',
    'django.contrib.sites',
    'django.contrib.markup',
    'piston',
    # bv's internal apps
    'bv.server.accounts',
    'bv.server.lib',
    'bv.server.carpool',
    'bv.server.talks',
    'bv.server.rating',
    'bv.server.pages',
    'bv.server.utils',
    'bv.server.api',
    'bv.server.apiconsumers',
)

# OAuth is great, but user experience with it is a bit ... strange, so we 
# need to provide the same user interface (at least the same menus) on the 
# client and server side.
# As we can't acces to the definition of urls of the client, there is a need
# to specify them here, by hand.
# This is easilly modifiable here, and that make the separation of application
# (eg. between "oauth server" side and "default client") invisible to the end 
# user.
# DEFAULT_CLIENT_ROOT_URL = 'http://www.bisonvert.net',
DEFAULT_CLIENT_ROOT_URL = 'http://127.0.0.1:8095',
DEFAULT_CLIENT_URLS = {
    'talks' : {
        'add_message': '%s/talks/%s/add_message/',
        'list': '%s/talks/'
        # 'list': '%s/talks/list/'
    },
    'trips': {
        'mine': '%s/trips/mine/',
        'home': '%s',
        'list': '%s/trips/',
        # 'list': '%s/trips/list/',
    }, 
    'reports': {
        'list': '%s/ratings/',
    }
}

# Set oauth ignore dupe models to false to be a bit noiseless with our logs.
PISTON_IGNORE_DUPE_MODELS = True
OAUTH_AUTH_VIEW = 'bv.server.apiconsumers.views.oauth_auth_view'
DEFAULT_PAGINATION_COUNT = 10

#gdal and others from minitage
libs = [".so", ".dylib", ".a"]
if 'MT' in os.environ:
    geosfound = False
    gdalfound = False 
    for gd in os.environ['LD_LIBRARY_PATH'].split(':'):
        if 'geos' in gd and not geosfound:
            files = os.listdir(gd)
            for libext in libs:
                for f in files:
                    if f.endswith(libext) and ('geos_c' in f):
                        GEOS_LIBRARY_PATH = os.path.join(gd, f)
                        geosfound = True
                        break
                if geosfound:
                    break 
        if 'gdal' in gd and not gdalfound:
            files = os.listdir(gd)
            for libext in libs:
                for f in files:
                    if f.endswith(libext):
                        GDAL_LIBRARY_PATH = os.path.join(gd, f)
                        gdalfound = True
                        break
                if gdalfound:
                    break

