import os

from .local import *

ETHEREUM_NODE_URL = 'http://localhost:8545'

IPFS_HOST = 'https://ipfs.infura.io'

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'NAME':     'travisci',
            'USER':     'postgres',
            'PASSWORD': '',
            'HOST':     'localhost',
            'PORT':     '',
        }
    }
