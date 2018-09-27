from .base import *
from .events.olympia import ETH_EVENTS

CELERY_SEND_TASK_ERROR_EMAILS = False

SECRET_KEY = env('SECRET_KEY')

INSTALLED_APPS.append('gunicorn')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

ETHEREUM_NODE_URL = env('ETHEREUM_NODE_URL')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'celery_locking',
    }
}

# ------------------------------------------------------------------------------
# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
if env('EMAIL_HOST', default=None):
    EMAIL_HOST = env('EMAIL_HOST')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_PORT = env('EMAIL_PORT')
    EMAIL_USE_TLS = True
    EMAIL_SUBJECT_PREFIX = env('EMAIL_SUBJECT_PREFIX')
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
    SERVER_EMAIL = DEFAULT_FROM_EMAIL
    EMAIL_LOG_BACKEND = 'email_log.backends.EmailBackend'
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ADMINS = (
    ('Giacomo', 'giacomo.licari@gnosis.pm'),
    ('Denis', 'denis@gnosis.pm'),
    ('Uxío', 'uxio@gnosis.pm'),
)

# ------------------------------------------------------------------------------
# Tournament settings
# ------------------------------------------------------------------------------
TOURNAMENT_TOKEN = env('TOURNAMENT_TOKEN')
LMSR_MARKET_MAKER = env('LMSR_MARKET_MAKER')

# ------------------------------------------------------------------------------
# Token issuance (optional)
# ------------------------------------------------------------------------------
ETHEREUM_DEFAULT_ACCOUNT = env('ETHEREUM_DEFAULT_ACCOUNT', default=None)
ETHEREUM_DEFAULT_ACCOUNT_PRIVATE_KEY = env('ETHEREUM_DEFAULT_ACCOUNT_PRIVATE_KEY', default=None)
TOURNAMENT_TOKEN_ISSUANCE = env.int('TOURNAMENT_TOKEN_ISSUANCE', 200000000000000000000)
ISSUANCE_GAS = env.int('ISSUANCE_GAS', 2000000)
ISSUANCE_GAS_PRICE = env.int('ISSUANCE_GAS_PRICE', 50000000000)
