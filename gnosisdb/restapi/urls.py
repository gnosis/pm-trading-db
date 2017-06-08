from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^centralized-oracles/$', views.CentralizedOracleListView.as_view(), name='centralized-oracles'),
    url(r'^centralized-oracles/(?P<addr>[a-fA-F0-9]+)/$', views.CentralizedOracleFetchView.as_view(), name='centralized-oracles-by-address'),
    url(r'^ultimate-oracles/$', views.UltimateOracleListView.as_view(), name='ultimate-oracles'),
    url(r'^ultimate-oracles/(?P<addr>[a-fA-F0-9]+)/$', views.UltimateOracleFetchView.as_view(), name='ultimate-oracles-by-address'),
    url(r'^events/$', views.EventListView.as_view()),
    url(r'^events/(?P<addr>[a-fA-F0-9]+)/$', views.EventFetchView.as_view()),
    url(r'^markets/$', views.MarketListView.as_view()),
    url(r'^markets/(?P<addr>[a-fA-F0-9]+)/$', views.MarketFetchView.as_view()),
    url(r'^factories/$', views.factories_view),
]
