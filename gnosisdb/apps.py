# -*- coding: utf-8 -*-
from celery import Celery
from django.apps import AppConfig
from django.conf import settings

app = Celery('ether-logs')


class GnosisdbConfig(AppConfig):
    name = 'gnosisdb'

    def ready(self):
        app.config_from_object('django.conf:settings')
        app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, force=True)
