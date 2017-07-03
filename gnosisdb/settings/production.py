from gnosisdb.settings.base import *
import os

CELERY_SEND_TASK_ERROR_EMAILS = True

# ------------------------------------------------------------------------------
# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_HOST=os.environ['EMAIL_HOST']
EMAIL_HOST_PASSWORD=os.environ['EMAIL_HOST_PASSWORD']
EMAIL_HOST_USER=os.environ['EMAIL_HOST_USER']
EMAIL_PORT=os.environ['EMAIL_PORT']
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = os.environ['EMAIL_SUBJECT_PREFIX']
DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_BACKEND = 'email_log.backends.EmailBackend'
EMAIL_LOG_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ADMINS = (
    ('Giacomo', 'giacomo.licari@gnosis.pm'),
    ('Denis', 'denis@gnosis.pm'),
)