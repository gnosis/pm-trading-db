import os

from .local import *

# Insert your rpc config here
ETHEREUM_NODE_HOST = 'localhost'
ETHEREUM_NODE_PORT = 8545
ETHEREUM_NODE_SSL = 0

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
