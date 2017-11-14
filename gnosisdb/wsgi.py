"""
WSGI config for dapp project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
from whitenoise.django import DjangoWhiteNoise

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.production")
os.environ["CELERY_LOADER"] = "django"

_application = get_wsgi_application()

application = DjangoWhiteNoise(_application)