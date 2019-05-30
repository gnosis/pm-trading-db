import environ

ROOT_DIR = environ.Path(__file__) - 3  # (/pm-trading-db/config/settings/base.py - 3 = /pm-trading-db)
APPS_DIR = ROOT_DIR.path('tradingdb')

env = environ.Env()

READ_DOT_ENV_FILE = env.bool('DJANGO_READ_DOT_ENV_FILE', default=False)
DOT_ENV_FILE = env('DJANGO_DOT_ENV_FILE', default=None)
if READ_DOT_ENV_FILE or DOT_ENV_FILE:
    DOT_ENV_FILE = DOT_ENV_FILE or '.env_docker_compose'
    # OS environment variables take precedence over variables from .env_docker_compose
    env.read_env(str(ROOT_DIR.path(DOT_ENV_FILE)))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = 'UTC'
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

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
        'celery.worker.strategy': {
            'handlers': ['console'],
            'level': 'INFO' if DEBUG else 'WARNING',
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
STATIC_ROOT = env('STATIC_ROOT', default=str(ROOT_DIR('staticfiles')))
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

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
if 'DATABASE_URL' in env:
    DATABASES = {
        'default': env.db('DATABASE_URL'),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',                      # Or path to database file if using sqlite3.
            'USER': 'postgres',                      # Not used with sqlite3.
            'PASSWORD': '',                  # Not used with sqlite3.
            'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'config.urls'
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
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
# Celery
# ------------------------------------------------------------------------------
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')
INSTALLED_APPS += ['tradingdb.taskapp.celery.CeleryConfig']
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=REDIS_URL)
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ['json']
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = 'json'
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = 'json'

# ------------------------------------------------------------------------------
# ETHEREUM
# ------------------------------------------------------------------------------
ETH_BACKUP_BLOCKS = env.int('ETH_BACKUP_BLOCKS ', default=100)
ETH_PROCESS_BLOCKS = env.int('ETH_PROCESS_BLOCKS', default=100)
ETH_FILTER_PROCESS_BLOCKS = env.int('ETH_FILTER_PROCESS_BLOCKS', default=100000)

ETHEREUM_NODE_URL = env('ETHEREUM_NODE_URL', default='http://localhost:8545')
ETHEREUM_MAX_WORKERS = env.int('ETHEREUM_MAX_WORKERS', default=10)
ETHEREUM_MAX_BATCH_REQUESTS = env.int('ETHEREUM_MAX_BATCH_REQUESTS', default=500)

# ------------------------------------------------------------------------------
# IPFS
# ------------------------------------------------------------------------------
IPFS_HOST = env('IPFS_HOST', default='ipfs.infura.io')
IPFS_PORT = env('IPFS_PORT', default=5001)
IPFS_TIMEOUT = env('IPFS_TIMEOUT', default=120)
