import os
import time
from subprocess import PIPE, Popen

from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
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

    def get_lock(self):
        """
        :return: True if lock can be acquired, False otherwise
        """
        with transaction.atomic():
            daemon = Daemon.get_solo()
            locked = daemon.listener_lock

            if not locked:
                self.stdout.write(self.style.SUCCESS('LOCK acquired by db_dump task'))
                daemon.listener_lock = True
                daemon.save()
                return True
            else:
                self.stdout.write(self.style.SUCCESS('LOCK already being imported by another worker'))
                return False

    def release_lock(self):
        with transaction.atomic():
            daemon = Daemon.objects.select_for_update().first()
            daemon.listener_lock = False
            daemon.save()

    def handle(self, *args, **options):
        """
        In order to make a proper dump and avoid race conditions while dumping, the system must be stopped.
        """
        try:
            self.stdout.write(self.style.SUCCESS('Starting GnosisDB Dump'))
            db_name = os.environ.get('DATABASE_NAME', 'postgres')
            db_user = os.environ.get('DATABASE_USER', 'postgres')
            db_host = os.environ.get('DATABASE_HOST', 'localhost')
            db_password = os.environ.get('DATABASE_PASSWORD', None)
            filename = self.dump_path + "{}_{}_dump-{}.sqlc".format(db_name, db_user, timezone.now().strftime('%Y-%m-%d_%H:%M:%S'))

            for _ in range(self.n_retries):
                locked = self.get_lock()
                if locked:
                    break

                time.sleep(1)

            try:
                if locked:
                    cmd = "pg_dump -h {host} -d {db} -U {user} --compress=9 --format=c --file={file}".format(host=db_host,
                                                                                                             db=db_name,
                                                                                                             user=db_user,
                                                                                                             file=filename)
                    if db_password:
                        cmd = "PGPASSWORD={password} {command}".format(password=db_password, command=cmd)

                    self.stdout.write(self.style.SUCCESS('Executing command %s' % cmd))
                    process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                    stdout, stderr = process.communicate()
                    if process.returncode != 0:
                        raise Exception(stderr)
                    self.stdout.write(self.style.SUCCESS('GnosisDB db_dump completed and saved into: {}'.format(filename)))
                    # Send file via email to admins
                    self.send_email(filename)
            finally:
                if locked:
                    self.stdout.write(self.style.SUCCESS('Releasing LOCK acquired by db_dump task'))
                    self.release_lock()
                else:
                    self.stdout.write(self.style.ERROR('Could not get LOCK for db_dump task'))
        except Exception as e:
            self.stdout.write(self.style.ERROR('GnosisDB db_dump error: {}'.format(e.message)))
