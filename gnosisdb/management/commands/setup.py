from django.core.management.base import BaseCommand
from celery import Celery
from celery.schedules import crontab
from relationaldb.models import EventDescription
from django_eth_events.models import Daemon
from djcelery.models import PeriodicTask, IntervalSchedule


class Command(BaseCommand):
    help = 'Cleans the Relational Database and sets up all required configuration'

    def handle(self, *args, **options):
        EventDescription.objects.all().delete()
        daemon = Daemon.get_solo()
        daemon.block_number = 0
        daemon.last_error_block_number = 0
        daemon.save()
        self.stdout.write(self.style.SUCCESS('DB Successfully cleaned.'))        

        # auto-create celery task
        interval=IntervalSchedule(every=5, period='seconds')
        interval.save()
        if not PeriodicTask.objects.filter(task='django_eth_events.tasks.event_listener').count():
            PeriodicTask.objects.create(
                name='Event Listener', 
                task='django_eth_events.tasks.event_listener',
                interval=interval
            )
            self.stdout.write(self.style.SUCCESS('Created Periodic Task for Event Listener every 5s.'))
