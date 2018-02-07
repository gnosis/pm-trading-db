# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.test import TestCase
from gnosisdb.relationaldb.tasks import db_dump
from django.core import mail
from django_eth_events.factories import DaemonFactory
from django.test.utils import override_settings


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    ADMINS = (('Test', 'test@gnosis.pm'),)
)
class TestCelery(TestCase):

    def setUp(self):
        self.daemon = DaemonFactory()

    def test_db_dump(self):
        self.assertEquals(len(mail.outbox), 0)
        db_dump()
        self.assertEquals(len(mail.outbox), 1)

