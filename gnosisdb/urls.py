# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='GnosisDB API')

urlpatterns = [
    url(r'^$', schema_view),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('gnosisdb.restapi.urls', namespace='api'))
]

admin.autodiscover()
