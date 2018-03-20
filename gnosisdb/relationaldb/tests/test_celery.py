# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from django_eth_events.factories import DaemonFactory

from ..tasks import db_dump


@override_settings(
    ADMINS=(('Test', 'test@gnosis.pm'),)
)
class TestCelery(TestCase):

    def setUp(self):
        self.daemon = DaemonFactory()

    def test_db_dump(self):
        self.assertEqual(len(mail.outbox), 0)
        db_dump()
        self.assertEqual(len(mail.outbox), 1)
