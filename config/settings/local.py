from .base import *

SECRET_KEY = 'DEPeWJKeZfFOtgfFzjk5BVn5lixq9vcfad1axbLWpuap1jyIAH'
DEBUG = True

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
INSTALLED_APPS += ['debug_toolbar', ]

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Django Debug Toolbar config
INTERNAL_IPS = ['localhost', '127.0.0.1', '172.17.0.1', '172.18.0.1']
