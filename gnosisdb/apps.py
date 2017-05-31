# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from main import GnosisDB


class GnosisdbConfig(AppConfig):
    name = 'gnosisdb'

    def ready(self):
        super(GnosisdbConfig, self).ready()
        self.gnosisdb = GnosisDB()
