from subprocess import check_call, CalledProcessError
from datetime import datetime
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django_eth_events.models import Daemon, STATUS_CHOICES
import os


class Command(BaseCommand):
    help = 'Creates a dump of the entire database'
    dump_path = '/tmp/'

    def send_email(self, filename):
        # send email
        email = EmailMultiAlternatives(
            subject='[Olympia GnosisDB backup]',
            body='GnosisDB backup attached.',
            from_email=settings.SERVER_EMAIL,
            to=[a[1] for a in settings.ADMINS]
        )
        fd = open(filename, 'r')
        email.attach('GnosisDB_dump', fd.read(), 'text/plain')
        email.send()

    def handle(self, *args, **options):
        """
        In order to make a proper dump and avoid race conditions while dumping, the system must be stopped.
        """
        try:
            # pg_dump -U $username --format=c --file=$mydatabase.sqlc $dbname
            self.stdout.write(self.style.SUCCESS('Starting GnosisDB Dump'))
            daemon = Daemon.get_solo()
            system_status_before_dump = daemon.status
            if system_status_before_dump == STATUS_CHOICES[0][0]:
                # System is running, need to stop it
                daemon.status = STATUS_CHOICES[1][0]
                daemon.save()

            db_name = os.environ.get('DATABASE_NAME', 'postgres')
            db_user = os.environ.get('DATABASE_USER', 'postgres')
            filename = self.dump_path + "{}_{}_dump-{}.sqlc".format(db_name, db_user, datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
            try:
                # check_call("python manage.py dumpdata --all --indent=4 --output " + filename, shell=True)
                cmd = "pg_dump -U {} --format=c --file={} {}".format(db_user, filename, db_name)
                self.stdout.write(self.style.SUCCESS('Executing command %s' % cmd))
                check_call(cmd)
                self.stdout.write(self.style.SUCCESS('GnosisDB Dump completed and saved into: {}'.format(filename)))
                # Send file via email to admins
                self.send_email(filename)
            except CalledProcessError as e:
                self.stdout.write(self.style.ERROR('GnosisDB Dump error: {}'.format(e.message)))
            finally:
                # Restart the system if it was running before starting dumping
                if system_status_before_dump == STATUS_CHOICES[0][0]:
                    daemon.status = STATUS_CHOICES[0][0]
                    daemon.save()
        except Exception as e:
            self.stdout.write(self.style.ERROR('GnosisDB Dump error: {}'.format(e.message)))

    def handleOLD(self, *args, **options):
        """
        In order to make a proper dump and avoid race conditions while dumping, the system must be stopped.
        """
        try:
            self.stdout.write(self.style.SUCCESS('Starting GnosisDB Dump'))
            daemon = Daemon.get_solo()
            system_status_before_dump = daemon.status
            if system_status_before_dump == STATUS_CHOICES[0][0]:
                # System is running, need to stop it
                daemon.status = STATUS_CHOICES[1][0]
                daemon.save()

            filename = self.dump_path + "gnosisdb_dump-{}.json".format(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
            try:
                check_call("python manage.py dumpdata --all --indent=4 --output " + filename, shell=True)
                self.stdout.write(self.style.SUCCESS('GnosisDB Dump completed and saved into: {}'.format(filename)))
                # Send file via email to admins
                self.send_email(filename)
            except CalledProcessError as e:
                self.stdout.write(self.style.ERROR('GnosisDB Dump error: {}'.format(e.message)))
            finally:
                # Restart the system if it was running before starting dumping
                if system_status_before_dump == STATUS_CHOICES[0][0]:
                    daemon.status = STATUS_CHOICES[0][0]
                    daemon.save()
        except Exception as e:
            self.stdout.write(self.style.ERROR('GnosisDB Dump error: {}'.format(e.message)))