from django.conf.urls import url

from . import views

app_name = "restapi"

timestamp_regex = '\\d{4}[-]?\\d{1,2}[-]?\\d{1,2} \\d{1,2}:\\d{1,2}:\\d{1,2}'

urlpatterns = [
    url(r'^about/$', views.about_view, name='about'),
    url(r'^centralized-oracles/$', views.CentralizedOracleListView.as_view(), name='centralized-oracles'),
    url(r'^centralized-oracles/(0x)?(?P<oracle_address>[a-fA-F0-9]+)/$', views.CentralizedOracleFetchView.as_view(), name='centralized-oracles-by-address'),
    url(r'^events/$', views.EventListView.as_view(), name='events'),
    url(r'^events/(0x)?(?P<event_address>[a-fA-F0-9]+)/$', views.EventFetchView.as_view(), name='events-by-address'),
    url(r'^markets/$', views.MarketListView.as_view(), name='markets'),
    url(r'^markets/(0x)?(?P<market_address>[a-fA-F0-9]+)/$', views.MarketFetchView.as_view(), name='markets-by-name'),
    url(r'^markets/(0x)?(?P<market_address>[a-fA-F0-9]+)/shares/$', views.AllMarketSharesView.as_view(), name='all-shares'),
    url(r'^markets/(0x)?(?P<market_address>[a-fA-F0-9]+)/shares/(0x)?(?P<owner_address>[a-fA-F0-9]+)/$', views.MarketSharesView.as_view(), name='shares-by-owner'),
    url(r'^markets/(0x)?(?P<market_address>[a-fA-F0-9]+)/trades/$', views.MarketTradesView.as_view(), name='trades-by-market'),
    url(r'^markets/(0x)?(?P<market_address>[a-fA-F0-9]+)/trades/(0x)?(?P<owner_address>[a-fA-F0-9]+)/$', views.MarketParticipantTradesView.as_view(), name='trades-by-owner'),
    url(r'^account/(0x)?(?P<account_address>[a-fA-F0-9]+)/trades/$', views.AccountTradesView.as_view(), name='trades-by-account'),
    url(r'^account/(0x)?(?P<account_address>[a-fA-F0-9]+)/shares/$', views.AccountSharesView.as_view(), name='shares-by-account'),
    url(r'^factories/$', views.factories_view, name='factories'),
    url(r'^scoreboard/$', views.ScoreboardView.as_view(), name='scoreboard'),
    url(r'^scoreboard/(0x)?(?P<account_address>[a-fA-F0-9]+)$', views.ScoreboardUserView.as_view(), name='scoreboard'),
]
