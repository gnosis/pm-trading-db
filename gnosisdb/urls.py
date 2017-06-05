# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url, include
from django.contrib import admin
from settings import base

import views


urlpatterns = [
    # url(r'^' + base.API_PREFIX + '/$', views.CreateView.as_view(), name='create'),
    url(r'^admin/', include(admin.site.urls))
]

admin.autodiscover()
