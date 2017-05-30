# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.test import TestCase
from gnosisdb.GnosisDB import GnosisDB

class TestGnosisDB(TestCase):

    def setUp(self):
        self.app = GnosisDB()

    def test_gnosisdb(self):
        print "OK"
