import os

import environ

TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
USE_TZ = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
# SITE_ID = 1

DEBUG = bool(int(os.environ.get('DEBUG', 0)))

ROOT_DIR = environ.Path(__file__) - 3  # (/a/b/myfile.py - 3 = /)
APPS_DIR = ROOT_DIR.path('tradingdb')

DJANGO_APPS = [
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.staticfiles',

    # Useful template tags:
    # 'django.contrib.humanize',

    # Admin
    'django.contrib.admin',
    'django.contrib.admindocs',
]

THIRD_PARTY_APPS = [
    'django_filters',
    'corsheaders',
    'django_celery_beat',
    'rest_framework',
    'rest_framework_swagger',
    'solo',
]

GNOSIS_APPS = [
    'django_eth_events',
    'django_google_authenticator',
]

LOCAL_APPS = [
    'tradingdb.chainevents.apps.ChainEventsConfig',
    'tradingdb.gnosis.apps.GnosisConfig',
    'tradingdb.ipfs.apps.IpfsConfig',
    'tradingdb.relationaldb.apps.RelationalDbConfig',
    'tradingdb.restapi.apps.RestApiConfig',
    'tradingdb.taskapp.celery.CeleryConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + GNOSIS_APPS + LOCAL_APPS


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
]

LOGGING = {
    'version': 1,
    # 'disable_existing_loggers': False,  # For Sentry
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] [%(processName)s] %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'django': {
            'handlers': ['console', 'mail_admins'],
            'propagate': True,
            'level': 'ERROR',
        },
    }
}

TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

CORS_ORIGIN_ALLOW_ALL = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = os.environ.get('STATIC_ROOT', str(ROOT_DIR('staticfiles')))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': 'db',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    }
}

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

# Filtering
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'PAGE_SIZE': 100,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
}

# ------------------------------------------------------------------------------
# RABBIT MQ
# ------------------------------------------------------------------------------
RABBIT_HOSTNAME = 'rabbit'
RABBIT_USER = 'tradingdb'
RABBIT_PASSWORD = 'tradingdb'
RABBIT_PORT = '5672'
BROKER_URL = 'amqp://{user}:{password}@{hostname}:{port}'.format(
    user=RABBIT_USER,
    password=RABBIT_PASSWORD,
    hostname=RABBIT_HOSTNAME,
    port=RABBIT_PORT
)

BROKER_POOL_LIMIT = 1
BROKER_CONNECTION_TIMEOUT = 10

CELERY_RESULT_SERIALIZER = 'json'
# configure queues, currently we have only one
CELERY_DEFAULT_QUEUE = 'default'

# Sensible settings for celery
CELERY_ALWAYS_EAGER = False
CELERY_ACKS_LATE = True
CELERY_TASK_PUBLISH_RETRY = True
CELERY_DISABLE_RATE_LIMITS = False

# By default we will ignore result
# If you want to see results and try out tasks interactively, change it to False
# Or change this setting on tasks level
CELERY_IGNORE_RESULT = False
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERY_TASK_RESULT_EXPIRES = 200
# Don't use pickle as serializer, json is much safer
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['application/json']
CELERYD_HIJACK_ROOT_LOGGER = False
CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_MAX_TASKS_PER_CHILD = 10
CELERY_LOCK_EXPIRE = 60

# ------------------------------------------------------------------------------
# ETHEREUM
# ------------------------------------------------------------------------------
ETH_BACKUP_BLOCKS = int(os.environ.get('ETH_BACKUP_BLOCKS ', 100))
ETH_PROCESS_BLOCKS = int(os.environ.get('ETH_PROCESS_BLOCKS', 100))

ETHEREUM_NODE_URL = 'http://172.17.0.1:8545'
ETHEREUM_MAX_WORKERS = int(os.environ.get('ETHEREUM_MAX_WORKERS', 10))
ETHEREUM_MAX_BATCH_REQUESTS = int(os.environ.get('ETHEREUM_MAX_BATCH_REQUESTS ', 500))

# ------------------------------------------------------------------------------
# IPFS
# ------------------------------------------------------------------------------
IPFS_HOST = 'http://ipfs'  # 'ipfs'
IPFS_PORT = 5001
