from .local import *

# Insert your rpc config here
ETHEREUM_NODE_HOST = 'localhost'
ETHEREUM_NODE_PORT = 8545
ETHEREUM_NODE_SSL = 0

IPFS_HOST = 'http://localhost'

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
