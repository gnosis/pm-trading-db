# -*- coding: utf-8 -*-
from .base import *

SECRET_KEY = 'DEPeWJKeZfFOtgfFzjk5BVn5lixq9vcfad1axbLWpuap1jyIAH'
DEBUG = True

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
INSTALLED_APPS += ['debug_toolbar', ]

TOURNAMENT_TOKEN = '254dffcd3277c0b1660f6d42efbb754edababc2b'
ETHEREUM_PRIVATE_KEY = '4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Django Debug Toolbar config
INTERNAL_IPS = ['localhost', '127.0.0.1', '172.17.0.1', '172.18.0.1']
