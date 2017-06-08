# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from settings.base import *
import sys


SECRET_KEY = 'testtest'
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'solo',
    'gnosisdb',
    'djcelery',
    'relationaldb',
    'rest_framework',
    'restapi',
    'eth'
)

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOGGING={
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}


TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
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
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

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

ROOT_URLCONF = 'gnosisdb.urls'

# Filtering
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}

# Celery
INSTALLED_APPS += ('kombu.transport.django',)
ETHEREUM_NODE_HOST='kovan.infura.io'
ETHEREUM_NODE_PORT = 443
ETHEREUM_NODE_SSL = 1

RABBIT_HOSTNAME = 'rabbit'
RABBIT_USER = 'gnosisdb'
RABBIT_PASSWORD = 'gnosisdb'
RABBIT_PORT = '5672'
BROKER_URL = 'amqp://{user}:{password}@{hostname}:{port}'.format(
    user=RABBIT_USER,
    password=RABBIT_PASSWORD,
    hostname=RABBIT_HOSTNAME,
    port=RABBIT_PORT
)

BROKER_POOL_LIMIT = 1
BROKER_CONNECTION_TIMEOUT = 10

# Celery configuration
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'djcelery.backends.cache:CacheBackend'
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
CELERY_SEND_TASK_ERROR_EMAILS = False
CELERY_TASK_RESULT_EXPIRES = 600
# Don't use pickle as serializer, json is much safer
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['application/json']
CELERYD_HIJACK_ROOT_LOGGER = False
CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_MAX_TASKS_PER_CHILD = 1000


# GnosisDB Contract Addresses
GNOSISDB_FACTORIES = [
    {
        'address': '0x254dffcd3277c0b1660f6d42efbb754edababc2b',
        'name': 'Centralized Oracle Factory',
        'abi': '[{"inputs": [], "constant": true, "name": "outcome", "payable": false, "outputs": [{"type": "int256", "name": ""}], "type": "function"}, {"inputs": [{"type": "int256", "name": "_outcome"}], "constant": false, "name": "setOutcome", "payable": false, "outputs": [], "type": "function"}, {"inputs": [], "constant": true, "name": "getOutcome", "payable": false, "outputs": [{"type": "int256", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "owner", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [{"type": "address", "name": "_owner"}], "constant": false, "name": "replaceOwner", "payable": false, "outputs": [], "type": "function"}, {"inputs": [], "constant": true, "name": "ipfsHash", "payable": false, "outputs": [{"type": "bytes", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "isSet", "payable": false, "outputs": [{"type": "bool", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "isOutcomeSet", "payable": false, "outputs": [{"type": "bool", "name": ""}], "type": "function"}, {"inputs": [{"type": "address", "name": "_owner"}, {"type": "bytes", "name": "_ipfsHash"}], "type": "constructor", "payable": false}]'
    },
    {
        'address': '0x5b1869d9a4c187f2eaa108f3062412ecf0526b24',
        'name': 'Event Factory',
        'abi': '[{"inputs": [{"type": "address", "name": "collateralToken"}, {"type": "address", "name": "oracle"}, {"type": "int256", "name": "lowerBound"}, {"type": "int256", "name": "upperBound"}], "constant": false, "name": "createScalarEvent", "payable": false, "outputs": [{"type": "address", "name": "eventContract"}], "type": "function"}, {"inputs": [{"type": "bytes32", "name": ""}], "constant": true, "name": "categoricalEvents", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [{"type": "bytes32", "name": ""}], "constant": true, "name": "scalarEvents", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [{"type": "address", "name": "collateralToken"}, {"type": "address", "name": "oracle"}, {"type": "uint8", "name": "outcomeCount"}], "constant": false, "name": "createCategoricalEvent", "payable": false, "outputs": [{"type": "address", "name": "eventContract"}], "type": "function"}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type": "address", "name": "categoricalEvent"}, {"indexed": false, "type": "address", "name": "collateralToken"}, {"indexed": false, "type": "address", "name": "oracle"}, {"indexed": false, "type": "uint8", "name": "outcomeCount"}], "type": "event", "name": "CategoricalEventCreation", "anonymous": false}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type": "address", "name": "scalarEvent"}, {"indexed": false, "type": "address", "name": "collateralToken"}, {"indexed": false, "type": "address", "name": "oracle"}, {"indexed": false, "type": "int256", "name": "lowerBound"}, {"indexed": false, "type": "int256", "name": "upperBound"}], "type": "event", "name": "ScalarEventCreation", "anonymous": false}]'
    },
    {
        'address': '0x9561c133dd8580860b6b7e504bc5aa500f0f06a7',
        'name': 'Default Market Factory',
        'abi': '[{"inputs": [{"type": "address", "name": "eventContract"}, {"type": "address", "name": "marketMaker"}, {"type": "uint256", "name": "fee"}], "constant": false, "name": "createMarket", "payable": false, "outputs": [{"type": "address", "name": "market"}], "type": "function"}, {"inputs": [{"indexed": true, "type": "address", "name": "creator"}, {"indexed": false, "type": "address", "name": "market"}, {"indexed": false, "type": "address", "name": "eventContract"}, {"indexed": false, "type": "address", "name": "marketMaker"}, {"indexed": false, "type": "uint256", "name": "fee"}], "type": "event", "name": "MarketCreation", "anonymous": false}]'
    }
]

GNOSISDB_ABIS = [
    {
        'name': 'Centralized Oracle',
        'abi': '[{"inputs": [], "constant": true, "name": "outcome", "payable": false, "outputs": [{"type": "int256", "name": ""}], "type": "function"}, {"inputs": [{"type": "int256", "name": "_outcome"}], "constant": false, "name": "setOutcome", "payable": false, "outputs": [], "type": "function"}, {"inputs": [], "constant": true, "name": "getOutcome", "payable": false, "outputs": [{"type": "int256", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "owner", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [{"type": "address", "name": "_owner"}], "constant": false, "name": "replaceOwner", "payable": false, "outputs": [], "type": "function"}, {"inputs": [], "constant": true, "name": "ipfsHash", "payable": false, "outputs": [{"type": "bytes", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "isSet", "payable": false, "outputs": [{"type": "bool", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "isOutcomeSet", "payable": false, "outputs": [{"type": "bool", "name": ""}], "type": "function"}, {"inputs": [{"type": "address", "name": "_owner"}, {"type": "bytes", "name": "_ipfsHash"}], "type": "constructor", "payable": false}]'
    },
    {
        'name': 'Categorical Event',
        'abi': '[{"inputs": [], "constant": true, "name": "isWinningOutcomeSet", "payable": false, "outputs": [{"type": "bool", "name": ""}], "type": "function"}, {"inputs": [{"type": "uint256", "name": "collateralTokenCount"}], "constant": false, "name": "buyAllOutcomes", "payable": false, "outputs": [], "type": "function"}, {"inputs": [{"type": "address", "name": "owner"}], "constant": true, "name": "getOutcomeTokenDistribution", "payable": false, "outputs": [{"type": "uint256[]", "name": "outcomeTokenDistribution"}], "type": "function"}, {"inputs": [{"type": "uint256", "name": "outcomeTokenCount"}], "constant": false, "name": "sellAllOutcomes", "payable": false, "outputs": [], "type": "function"}, {"inputs": [], "constant": true, "name": "oracle", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "getOutcomeCount", "payable": false, "outputs": [{"type": "uint8", "name": ""}], "type": "function"}, {"inputs": [{"type": "uint256", "name": ""}], "constant": true, "name": "outcomeTokens", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "winningOutcome", "payable": false, "outputs": [{"type": "int256", "name": ""}], "type": "function"}, {"inputs": [], "constant": false, "name": "redeemWinnings", "payable": false, "outputs": [{"type": "uint256", "name": "winnings"}], "type": "function"}, {"inputs": [], "constant": true, "name": "collateralToken", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "getEventHash", "payable": false, "outputs": [{"type": "bytes32", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "getOutcomeTokens", "payable": false, "outputs": [{"type": "address[]", "name": ""}], "type": "function"}, {"inputs": [], "constant": false, "name": "setWinningOutcome", "payable": false, "outputs": [], "type": "function"}, {"inputs": [{"type": "address", "name": "_collateralToken"}, {"type": "address", "name": "_oracle"}, {"type": "uint8", "name": "outcomeCount"}], "type": "constructor", "payable": false}]'
    },
    {
        'name': 'Scalar Event',
        'abi': '[{"inputs": [], "constant": true, "name": "isWinningOutcomeSet", "payable": false, "outputs": [{"type": "bool", "name": ""}], "type": "function"}, {"inputs": [{"type": "uint256", "name": "collateralTokenCount"}], "constant": false, "name": "buyAllOutcomes", "payable": false, "outputs": [], "type": "function"}, {"inputs": [], "constant": true, "name": "LONG", "payable": false, "outputs": [{"type": "uint8", "name": ""}], "type": "function"}, {"inputs": [{"type": "address", "name": "owner"}], "constant": true, "name": "getOutcomeTokenDistribution", "payable": false, "outputs": [{"type": "uint256[]", "name": "outcomeTokenDistribution"}], "type": "function"}, {"inputs": [], "constant": true, "name": "OUTCOME_RANGE", "payable": false, "outputs": [{"type": "uint16", "name": ""}], "type": "function"}, {"inputs": [{"type": "uint256", "name": "outcomeTokenCount"}], "constant": false, "name": "sellAllOutcomes", "payable": false, "outputs": [], "type": "function"}, {"inputs": [], "constant": true, "name": "oracle", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "getOutcomeCount", "payable": false, "outputs": [{"type": "uint8", "name": ""}], "type": "function"}, {"inputs": [{"type": "uint256", "name": ""}], "constant": true, "name": "outcomeTokens", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "winningOutcome", "payable": false, "outputs": [{"type": "int256", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "lowerBound", "payable": false, "outputs": [{"type": "int256", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "SHORT", "payable": false, "outputs": [{"type": "uint8", "name": ""}], "type": "function"}, {"inputs": [], "constant": false, "name": "redeemWinnings", "payable": false, "outputs": [{"type": "uint256", "name": "winnings"}], "type": "function"}, {"inputs": [], "constant": true, "name": "upperBound", "payable": false, "outputs": [{"type": "int256", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "collateralToken", "payable": false, "outputs": [{"type": "address", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "getEventHash", "payable": false, "outputs": [{"type": "bytes32", "name": ""}], "type": "function"}, {"inputs": [], "constant": true, "name": "getOutcomeTokens", "payable": false, "outputs": [{"type": "address[]", "name": ""}], "type": "function"}, {"inputs": [], "constant": false, "name": "setWinningOutcome", "payable": false, "outputs": [], "type": "function"}, {"inputs": [{"type": "address", "name": "_collateralToken"}, {"type": "address", "name": "_oracle"}, {"type": "int256", "name": "_lowerBound"}, {"type": "int256", "name": "_upperBound"}], "type": "constructor", "payable": false}]'
    }
]