import os

from .base import *
from .events.olympia import ETH_EVENTS

CELERY_SEND_TASK_ERROR_EMAILS = False

SECRET_KEY = os.environ['SECRET_KEY']

INSTALLED_APPS.append("gunicorn")

DEBUG = bool(int(os.environ.get('DEBUG', '0')))

ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USER'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': os.environ['DATABASE_HOST'],
        'PORT': os.environ['DATABASE_PORT'],
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
if 'EMAIL_HOST' in os.environ:
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_PORT = os.environ['EMAIL_PORT']
    EMAIL_USE_TLS = True
    EMAIL_SUBJECT_PREFIX = os.environ['EMAIL_SUBJECT_PREFIX']
    DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
    SERVER_EMAIL = DEFAULT_FROM_EMAIL
    EMAIL_LOG_BACKEND = 'email_log.backends.EmailBackend'
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ADMINS = (
    ('Giacomo', 'giacomo.licari@gnosis.pm'),
    ('Denis', 'denis@gnosis.pm'),
    ('Uxío', 'uxio@gnosis.pm'),
)

# ------------------------------------------------------------------------------
# RABBIT MQ
# ------------------------------------------------------------------------------
RABBIT_HOSTNAME = os.environ['RABBIT_HOSTNAME']
RABBIT_USER = os.environ['RABBIT_USER']
RABBIT_PASSWORD = os.environ['RABBIT_PASSWORD']
RABBIT_PORT = os.environ['RABBIT_PORT']
RABBIT_QUEUE = os.environ['RABBIT_QUEUE']
BROKER_URL = 'amqp://{user}:{password}@{hostname}:{port}/{queue}'.format(
    user=RABBIT_USER,
    password=RABBIT_PASSWORD,
    hostname=RABBIT_HOSTNAME,
    port=RABBIT_PORT,
    queue=RABBIT_QUEUE
)

# ------------------------------------------------------------------------------
# ETHEREUM
# ------------------------------------------------------------------------------
ETHEREUM_NODE_URL = os.environ['ETHEREUM_NODE_URL']

# ------------------------------------------------------------------------------
# IPFS
# ------------------------------------------------------------------------------
IPFS_HOST = os.environ['IPFS_HOST']
IPFS_PORT = os.environ['IPFS_PORT']

# ------------------------------------------------------------------------------
# Tournament settings
# ------------------------------------------------------------------------------
TOURNAMENT_TOKEN = os.environ['TOURNAMENT_TOKEN']
LMSR_MARKET_MAKER = os.environ['LMSR_MARKET_MAKER']

# ------------------------------------------------------------------------------
# Token issuance (optional)
# ------------------------------------------------------------------------------
ETHEREUM_DEFAULT_ACCOUNT = os.environ.get('ETHEREUM_DEFAULT_ACCOUNT')
ETHEREUM_DEFAULT_ACCOUNT_PRIVATE_KEY = os.environ.get('ETHEREUM_DEFAULT_ACCOUNT_PRIVATE_KEY')
TOURNAMENT_TOKEN_ISSUANCE = os.environ.get('TOURNAMENT_TOKEN_ISSUANCE', '200000000000000000000')
ISSUANCE_GAS = int(os.environ.get('ISSUANCE_GAS', 2000000))
ISSUANCE_GAS_PRICE = int(os.environ.get('ISSUANCE_GAS_PRICE', 50000000000))
