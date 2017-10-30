from subprocess import check_call, CalledProcessError
from datetime import datetime
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a dump of the entire database'

    def send_email(self, filename):
        # send email
        email = EmailMultiAlternatives(
            subject='[Olympia GnosisDB backup]',
            body='GnosisDB backup atteched.',
            from_email=settings.SERVER_EMAIL,
            to=[a[1] for a in settings.ADMINS]
        )
        fd = open(filename, 'r')
        email.attach('GnosisDB_dump', fd.read(), 'text/plain')
        email.send()

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Starting GnosisDB Dump'))
            filename = "/tmp/gnosisdb_dump-{}.json".format(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
            try:
                check_call("python manage.py dumpdata --all --indent=4 --output " + filename, shell=True)
                self.stdout.write(self.style.SUCCESS('GnosisDB Dump completed and saved into: {}'.format(filename)))
                # Send file via email to admins
                self.send_email(filename)
            except CalledProcessError as e:
                self.stdout.write(self.style.ERROR('GnosisDB Dump error: {}'.format(e.message)))
        except Exception as e:
            self.stdout.write(self.style.ERROR('GnosisDB Dump error: {}'.format(e.message)))
