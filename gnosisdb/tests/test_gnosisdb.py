# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.core.urlresolvers import reverse
from bitcoin import ecdsa_raw_sign
from ethereum.utils import sha3
from json import dumps
from gnosisdb.main import GnosisDB


class TestGnosisDB(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestGnosisDB, self).__init__(*args, **kwargs)
        self.gnosisdb = None

    def setUp(self):
        self.gnosisdb = GnosisDB()
        self.v, self.r, self.s = ecdsa_raw_sign(sha3('test').encode('hex'), sha3(b'safe very safe').encode('hex'))

    def test_app_running(self):
        self.assertIsNotNone(self.gnosisdb)
