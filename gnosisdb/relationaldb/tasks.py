from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import mail_admins
from relationaldb.models import TournamentParticipant
from django_eth_events.tasks import cache_lock
import traceback
from django.core.management import call_command, settings

logger = get_task_logger(__name__)

oid = 'TOURNAMENT_BLOCK'


def send_email(message):
    logger.info('Couldnt issue User tokens due to: {}'.format(message))
    # send email
    mail_admins('[Olympia Issuance Error] ', message)


@shared_task
def issue_tokens():
    with cache_lock('tournament_issuance', oid) as acquired:
        if acquired:
            participants = TournamentParticipant.objects.filter(tokens_issued=False)[:50]
            if len(participants):
                try:
                    participant_addresses = ",".join(participant.address for participant in participants)
                    call_command('issue_tournament_tokens', participant_addresses , settings.TOURNAMENT_TOKEN_ISSUANCE)
                    for participant in participants:
                        participant.tokens_issued = True
                        participant.save()
                except Exception as err:
                    logger.error(str(err))
                    send_email(traceback.format_exc())
            else:
                logger.info("No new tournament participants")




