import time

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Command(BaseCommand):
    help = 'Cleans the Relational Database and sets up all required configuration'

    def handle(self, *args, **options):
        PeriodicTask.objects.filter(task='django_eth_events.tasks.event_listener').delete()
        time.sleep(5)
        call_command('cleandatabase')
        call_command('resync_daemon')
        self.stdout.write(self.style.SUCCESS('Making sure no process was running'))
        time.sleep(5)
        call_command('cleandatabase')
        call_command('resync_daemon')

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
