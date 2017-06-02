# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from gnosisdb.settings.base import *
import sys


SECRET_KEY = 'testtest'
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'solo',
    'gnosisdb',
    'gnosisdb.tests',
    'django_ether_logs'
)

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': 'db',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

ROOT_URLCONF = 'urls'

# DJANGO ETHEREUM WATCHER CONFIGURATION
# ------------------------------------------------------------------------------
# from events.models import Alert as DAppAlertModel
ALERT_MODEL_APP = 'events'
ALERT_MODEL = 'Alert'
CALLBACK_PER_BLOCK = None
CALLBACK_PER_EXEC = None