import time

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from django_eth_events.models import Block, Daemon


class Command(BaseCommand):
    help = 'Cleans the Relational Database and sets up all required configuration'

    def add_arguments(self, parser):
        parser.add_argument('--start-block-number', type=int, required=False)

    def handle(self, *args, start_block_number, **options):
        PeriodicTask.objects.filter(task='django_eth_events.tasks.event_listener').delete()
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
        interval = IntervalSchedule(every=5, period='seconds')
        interval.save()
        if not PeriodicTask.objects.filter(task='django_eth_events.tasks.event_listener').count():
            PeriodicTask.objects.create(
                name='Event Listener',
                task='django_eth_events.tasks.event_listener',
                interval=interval
            )
            self.stdout.write(self.style.SUCCESS('Created Periodic Task for Event Listener every 5s'))
