from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import mail_admins
from django.core.management import call_command
import traceback


logger = get_task_logger(__name__)


def send_email(message):
    logger.info('Task error: {}'.format(message))
    # send email
    mail_admins('[GnosisDB Error] ', message)


@shared_task
def db_dump():
    """
    The task creates a dump of the database
    """
    try:
        call_command('db_dump')
    except Exception as err:
        logger.error(str(err))
        send_email(traceback.format_exc())



