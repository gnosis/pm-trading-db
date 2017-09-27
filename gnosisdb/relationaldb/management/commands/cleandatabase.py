from django.core.management.base import BaseCommand
from relationaldb.models import EventDescription


class Command(BaseCommand):
    help = 'Cleans the Relational Database'

    def handle(self, *args, **options):
        EventDescription.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('DB Successfully cleaned'))
