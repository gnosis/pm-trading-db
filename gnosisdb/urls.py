# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponse
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='GnosisDB API')

urlpatterns = [
    url(r'^$', schema_view),
    url(r'', include('django_google_authenticator.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^api/', include('gnosisdb.restapi.urls', namespace='api')),
    url(r'^check/', lambda request: HttpResponse("Ok")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(
        url(r'^__debug__/', include(debug_toolbar.urls))
    )

admin.autodiscover()
