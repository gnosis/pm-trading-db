import os
import time
from datetime import datetime
from subprocess import PIPE, Popen

from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.db import transaction
from django_eth_events.models import Daemon


class Command(BaseCommand):
    help = 'Creates a dump of the entire database'
    dump_path = '/tmp/'
    n_retries = 3

    def send_email(self, filename):
        # send email
        email = EmailMultiAlternatives(
            subject='[Olympia GnosisDB backup]',
            body='GnosisDB backup attached.',
            from_email=settings.SERVER_EMAIL,
            to=[a[1] for a in settings.ADMINS]
        )
        email.attach_file(filename)
        email.send()

    def is_locked(self):
        locked = False

        with transaction.atomic():
            daemon = Daemon.get_solo()
            locked = daemon.listener_lock

            if not locked:
                self.stdout.write(self.style.SUCCESS('LOCK acquired by db_dump task'))
                daemon.listener_lock = True
                daemon.save()

        if locked:
            self.stdout.write(self.style.SUCCESS('LOCK already being imported by another worker'))

        return locked

    def handle(self, *args, **options):
        """
        In order to make a proper dump and avoid race conditions while dumping, the system must be stopped.
        """
        try:
            self.stdout.write(self.style.SUCCESS('Starting GnosisDB Dump'))
            locked = False
            db_name = os.environ.get('DATABASE_NAME', 'postgres')
            db_user = os.environ.get('DATABASE_USER', 'postgres')
            db_host = os.environ.get('DATABASE_HOST', 'localhost')
            db_password = os.environ.get('DATABASE_PASSWORD', None)
            filename = self.dump_path + "{}_{}_dump-{}.sqlc".format(db_name, db_user, datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))

            for _ in range(self.n_retries):
                locked = self.is_locked()
                if not locked:
                    break

                time.sleep(1)

            try:
                if not locked:
                    if not db_password:
                        cmd = "pg_dump -h {0} -d {1} -U {2} --format=c --file={3}".format(db_host, db_name, db_user, filename)
                    else:
                        cmd = "PGPASSWORD={0} pg_dump -h {1} -d {2} -U {3} --format=c --file={4}".format(db_password,
                                                                                                         db_host,
                                                                                                         db_name,
                                                                                                         db_user,
                                                                                                         filename)
                    self.stdout.write(self.style.SUCCESS('Executing command %s' % cmd))
                    process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                    stdout, stderr = process.communicate()
                    if process.returncode != 0:
                        raise Exception(stderr)
                    self.stdout.write(self.style.SUCCESS('GnosisDB Dump completed and saved into: {}'.format(filename)))
                    # Send file via email to admins
                    self.send_email(filename)
            except Exception as e:
                self.stdout.write(self.style.ERROR('GnosisDB Dump error: {}'.format(e.message)))
            finally:
                self.stdout.write(self.style.SUCCESS('Releasing LOCK acquired by db_dump task'))
                with transaction.atomic():
                    daemon = Daemon.objects.select_for_update().first()
                    daemon.listener_lock = False
                    daemon.save()
        except Exception as e:
            self.stdout.write(self.style.ERROR('GnosisDB Dump error: {}'.format(e.message)))
