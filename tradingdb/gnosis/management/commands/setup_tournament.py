import time

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from django_eth_events.models import Block, Daemon
from django_eth_events.utils import normalize_address_without_0x
from tradingdb.relationaldb.models import TournamentWhitelistedCreator


class Command(BaseCommand):
    help = 'Cleans the Relational Database and sets up all required configuration for tournament'

    def add_arguments(self, parser):
        parser.add_argument('--start-block-number', type=int, required=False)

    def handle(self, *args, start_block_number, **options):
        PeriodicTask.objects.filter(task__in=[
            'django_eth_events.tasks.event_listener',
            'tradingdb.relationaldb.tasks.calculate_scoreboard',
            'tradingdb.relationaldb.tasks.issue_tokens',
            'tradingdb.relationaldb.tasks.clear_issued_tokens_flag',
        ]).delete()
        time.sleep(5)
        call_command('cleandatabase')
        call_command('resync_daemon')
        self.stdout.write(self.style.SUCCESS('Making sure no process was running'))

        time.sleep(5)
        call_command('cleandatabase')
        call_command('resync_daemon')

        if start_block_number is not None:
            Block.objects.all().delete()

            daemon = Daemon.get_solo()
            daemon.block_number = start_block_number - 1
            daemon.save()

            self.stdout.write(self.style.SUCCESS('Restart processing at block {}'.format(start_block_number)))

        # auto-create celery task
        five_seconds_interval = IntervalSchedule(every=5, period='seconds')
        five_seconds_interval.save()

        ten_minutes_interval = IntervalSchedule(every=10, period='minutes')
        ten_minutes_interval.save()

        one_minute_interval = IntervalSchedule(every=1, period='minutes')
        one_minute_interval.save()

        one_day_interval = IntervalSchedule(every=1, period='days')
        one_day_interval.save()

        PeriodicTask.objects.create(
            name='Event Listener',
            task='django_eth_events.tasks.event_listener',
            interval=five_seconds_interval,
        )
        self.stdout.write(self.style.SUCCESS('Created Periodic Task for Event Listener every 5 seconds'))

        PeriodicTask.objects.create(
            name='Scoreboard Calculation',
            task='tradingdb.relationaldb.tasks.calculate_scoreboard',
            interval=ten_minutes_interval,
        )
        self.stdout.write(self.style.SUCCESS('Created Periodic Task for Scoreboard every 10 minutes'))

        PeriodicTask.objects.create(
            name='Token issuance',
            task='tradingdb.relationaldb.tasks.issue_tokens',
            interval=one_minute_interval,
        )
        self.stdout.write(self.style.SUCCESS('Created Periodic Task for Token Issuance every minute'))

        PeriodicTask.objects.create(
            name='Token issuance flag clear',
            task='tradingdb.relationaldb.tasks.clear_issued_tokens_flag',
            interval=one_day_interval,
        )
        self.stdout.write(self.style.SUCCESS('Created Periodic Task for Token Issuance flag clear every day'))

        TournamentWhitelistedCreator.objects.create(
            address=normalize_address_without_0x(settings.ETHEREUM_DEFAULT_ACCOUNT),
            enabled=True
        )
        self.stdout.write(
            self.style.SUCCESS('Added User {} to Tournament Whitelist'.format(settings.ETHEREUM_DEFAULT_ACCOUNT))
        )
