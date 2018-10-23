import os

import ethereum.utils
from django.conf import settings
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from tradingdb.relationaldb.models import (CentralizedOracle, Event, Market,
                                           Order, OutcomeTokenBalance,
                                           TournamentParticipant,
                                           TournamentWhitelistedCreator)
from tradingdb.version import __git_info__, __version__

from .filters import (CentralizedOracleFilter, DefaultPagination, EventFilter,
                      MarketFilter, MarketSharesFilter, MarketTradesFilter)
from .serializers import (CentralizedOracleSerializer, EventSerializer,
                          MarketSerializer, MarketTradesSerializer,
                          OlympiaScoreboardSerializer,
                          OutcomeTokenBalanceSerializer)


class AboutView(APIView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, format=None):
        ethereum_default_account_public_key = ethereum.utils.checksum_encode(ethereum.utils.privtoaddr(
            settings.ETHEREUM_DEFAULT_ACCOUNT_PRIVATE_KEY)) if settings.ETHEREUM_DEFAULT_ACCOUNT_PRIVATE_KEY else None
        content = {
            'git': __git_info__,
            'version': __version__,
            'settings': {
                'ethereum_node': {
                    'ETHEREUM_NODE_URL': settings.ETHEREUM_NODE_URL,
                    'ETHEREUM_MAX_WORKERS': settings.ETHEREUM_MAX_WORKERS,
                    'ETHEREUM_MAX_BATCH_REQUESTS': settings.ETHEREUM_MAX_BATCH_REQUESTS,
                    'ETH_BACKUP_BLOCKS': settings.ETH_BACKUP_BLOCKS,
                    'ETH_FILTER_PROCESS_BLOCKS': settings.ETH_FILTER_PROCESS_BLOCKS,
                    'ETH_PROCESS_BLOCKS': settings.ETH_PROCESS_BLOCKS,
                },
                'ipfs': {
                    'IPFS_HOST': settings.IPFS_HOST,
                    'IPFS_PORT': settings.IPFS_PORT,
                },
                'addresses': {
                    'CENTRALIZED_ORACLE_FACTORY': os.environ['CENTRALIZED_ORACLE_FACTORY'],
                    'EVENT_FACTORY': os.environ['EVENT_FACTORY'],
                    'MARKET_FACTORY': os.environ['MARKET_FACTORY'],
                    'TOURNAMENT_TOKEN': settings.TOURNAMENT_TOKEN,
                    'LMSR_MARKET_MAKER': settings.LMSR_MARKET_MAKER,
                    'UPORT_IDENTITY_MANAGER': os.environ['UPORT_IDENTITY_MANAGER'],
                    'GENERIC_IDENTITY_MANAGER_ADDRESS': os.environ['GENERIC_IDENTITY_MANAGER_ADDRESS'],
                },
                'issuance': {
                    'ETHEREUM_DEFAULT_ACCOUNT_PUBLIC_KEY': ethereum_default_account_public_key,
                }
            }
        }
        return Response(content)


class CentralizedOracleListView(generics.ListAPIView):
    serializer_class = CentralizedOracleSerializer
    filter_class = CentralizedOracleFilter
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = CentralizedOracle.objects.all().select_related(
            'event_description',
            'event_description__scalareventdescription',
            'event_description__categoricaleventdescription'
        )
        return queryset


class CentralizedOracleFetchView(generics.RetrieveAPIView):
    queryset = CentralizedOracle.objects.all()
    serializer_class = CentralizedOracleSerializer

    def get_object(self):
        return get_object_or_404(CentralizedOracle, address=self.kwargs['oracle_address'])


class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    filter_class = EventFilter
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = Event.objects.all().select_related(
            'oracle',
            'scalarevent',
            'scalarevent__oracle',
            'scalarevent__oracle__centralizedoracle',
            'scalarevent__oracle__centralizedoracle__event_description',
            'scalarevent__oracle__centralizedoracle__event_description__categoricaleventdescription',
            'scalarevent__oracle__centralizedoracle__event_description__scalareventdescription',
            'categoricalevent',
            'categoricalevent__oracle',
            'categoricalevent__oracle__centralizedoracle',
            'categoricalevent__oracle__centralizedoracle__event_description',
            'categoricalevent__oracle__centralizedoracle__event_description__categoricaleventdescription',
            'categoricalevent__oracle__centralizedoracle__event_description__scalareventdescription',
            'oracle__centralizedoracle',
            'oracle__centralizedoracle__event_description',
            'oracle__centralizedoracle__event_description__categoricaleventdescription',
            'oracle__centralizedoracle__event_description__scalareventdescription',
        )
        return queryset


class EventFetchView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_object(self):
        return get_object_or_404(Event, address=self.kwargs['event_address'])


class MarketListView(generics.ListAPIView):
    serializer_class = MarketSerializer
    filter_class = MarketFilter
    pagination_class = DefaultPagination

    def get_queryset(self):
        # Eager loading of related models
        queryset = Market.objects.all()
        queryset = queryset.select_related(
            'event',
            'event__oracle',
            'event__scalarevent',
            'event__scalarevent__oracle',
            'event__scalarevent__oracle__centralizedoracle',
            'event__scalarevent__oracle__centralizedoracle__event_description',
            'event__scalarevent__oracle__centralizedoracle__event_description__categoricaleventdescription',
            'event__scalarevent__oracle__centralizedoracle__event_description__scalareventdescription',
            'event__categoricalevent',
            'event__categoricalevent__oracle',
            'event__categoricalevent__oracle__centralizedoracle',
            'event__categoricalevent__oracle__centralizedoracle__event_description',
            'event__categoricalevent__oracle__centralizedoracle__event_description__categoricaleventdescription',
            'event__categoricalevent__oracle__centralizedoracle__event_description__scalareventdescription',
            'event__oracle__centralizedoracle',
            'event__oracle__centralizedoracle__event_description',
            'event__oracle__centralizedoracle__event_description__categoricaleventdescription',
            'event__oracle__centralizedoracle__event_description__scalareventdescription',
        )
        return queryset


class MarketFetchView(generics.RetrieveAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer

    def get_object(self):
        return get_object_or_404(Market, address=self.kwargs['market_address'])


@api_view(['GET'])
def factories_view(request):
    factories = {}
    for contract in settings.ETH_EVENTS:
        if 'PUBLISH' not in contract or not contract['PUBLISH']:
            continue
        address = contract['ADDRESSES'][0]
        index = contract['NAME']
        if 'PUBLISH_UNDER' in contract:
            pub_index = contract['PUBLISH_UNDER']
            if pub_index in factories:
                factories[pub_index][index] = address
            else:
                factories[pub_index] = {index: address}
        else:
            factories[index] = address

    return Response(factories)


class MarketSharesView(generics.ListAPIView):
    serializer_class = OutcomeTokenBalanceSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        market = get_object_or_404(Market, address=self.kwargs['market_address'])
        outcome_tokens = market.event.outcome_tokens.values_list('address', flat=True)
        return OutcomeTokenBalance.objects.filter(
            owner=self.kwargs['owner_address'],
            outcome_token__address__in=list(outcome_tokens)
        ).select_related(
            'outcome_token',
            'outcome_token__event',
            'outcome_token__event__oracle',
            'outcome_token__event__oracle__centralizedoracle',
            'outcome_token__event__oracle__centralizedoracle__event_description',
            'outcome_token__event__oracle__centralizedoracle__event_description__categoricaleventdescription',
            'outcome_token__event__oracle__centralizedoracle__event_description__scalareventdescription',
        )


class AllMarketSharesView(generics.ListAPIView):
    """
    Returns all outcome token balances (market shares) for all users in a market
    """
    serializer_class = OutcomeTokenBalanceSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        return OutcomeTokenBalance.objects.filter(
            outcome_token__address__in=list(
                Market.objects.get(
                    address=self.kwargs['market_address']
                ).event.outcome_tokens.values_list('address', flat=True)
            )
        ).select_related(
            'outcome_token',
            'outcome_token__event',
            'outcome_token__event__oracle',
            'outcome_token__event__oracle__centralizedoracle',
            'outcome_token__event__oracle__centralizedoracle__event_description',
            'outcome_token__event__oracle__centralizedoracle__event_description__categoricaleventdescription',
            'outcome_token__event__oracle__centralizedoracle__event_description__scalareventdescription',
        ).prefetch_related('outcome_token__event__markets')


class MarketParticipantTradesView(generics.ListAPIView):
    serializer_class = MarketTradesSerializer
    pagination_class = DefaultPagination
    filter_class = MarketTradesFilter

    def get_queryset(self):
        return Order.objects.filter(
            market=self.kwargs['market_address'],
            sender=self.kwargs['owner_address']
        ).select_related(
            'outcome_token',
            'outcome_token__event',
            'outcome_token__event__oracle',
            'outcome_token__event__oracle__centralizedoracle',
            'outcome_token__event__oracle__centralizedoracle__event_description',
            'outcome_token__event__oracle__centralizedoracle__event_description__categoricaleventdescription',
            'outcome_token__event__oracle__centralizedoracle__event_description__scalareventdescription',
        ).prefetch_related('outcome_token__event__markets')


class MarketTradesView(generics.ListAPIView):
    """
    Returns the orders (trades) for the given market address
    """
    serializer_class = MarketTradesSerializer
    pagination_class = DefaultPagination
    filter_class = MarketTradesFilter

    def get_queryset(self):
        # Check if Market exists
        get_list_or_404(Market, address=self.kwargs['market_address'])
        # return trades
        return Order.objects.filter(
            market=self.kwargs['market_address'],
        ).order_by('creation_block'
        ).select_related(
            'outcome_token',
            'outcome_token__event',
            'outcome_token__event__oracle',
            'outcome_token__event__oracle__centralizedoracle',
            'outcome_token__event__oracle__centralizedoracle__event_description',
            'outcome_token__event__oracle__centralizedoracle__event_description__categoricaleventdescription',
            'outcome_token__event__oracle__centralizedoracle__event_description__scalareventdescription',
        ).prefetch_related('outcome_token__event__markets')


class AccountTradesView(generics.ListAPIView):
    """
    Returns the orders (trades) for the given account address
    """
    serializer_class = MarketTradesSerializer
    pagination_class = DefaultPagination
    filter_class = MarketTradesFilter

    def get_queryset(self):
        return Order.objects.filter(
            sender=self.kwargs['account_address']
        ).select_related(
            'outcome_token',
            'outcome_token__event',
            'outcome_token__event__oracle',
            'outcome_token__event__oracle__centralizedoracle',
            'outcome_token__event__oracle__centralizedoracle__event_description',
            'outcome_token__event__oracle__centralizedoracle__event_description__categoricaleventdescription',
            'outcome_token__event__oracle__centralizedoracle__event_description__scalareventdescription',
        ).prefetch_related('outcome_token__event__markets')


class AccountSharesView(generics.ListAPIView):
    """
    Returns the shares for the given account address
    """
    serializer_class = OutcomeTokenBalanceSerializer
    pagination_class = DefaultPagination
    filter_class = MarketSharesFilter

    def get_queryset(self):
        return OutcomeTokenBalance.objects.filter(
            owner=self.kwargs['account_address'],
        ).select_related(
            'outcome_token',
            'outcome_token__event',
            'outcome_token__event__oracle',
            'outcome_token__event__oracle__centralizedoracle',
            'outcome_token__event__oracle__centralizedoracle__event_description',
            'outcome_token__event__oracle__centralizedoracle__event_description__categoricaleventdescription',
            'outcome_token__event__oracle__centralizedoracle__event_description__scalareventdescription',
        ).prefetch_related('outcome_token__event__markets')


# ========================================================
#                 Olympia
# ========================================================

class ScoreboardView(generics.ListAPIView):
    """Olympia tournament scoreboard view"""
    serializer_class = OlympiaScoreboardSerializer
    pagination_class = DefaultPagination
    queryset = TournamentParticipant.objects.all().order_by('current_rank').exclude(
        address__in=TournamentWhitelistedCreator.objects.all().values_list('address', flat=True)
    ).select_related('tournament_balance')


class ScoreboardUserView(generics.RetrieveAPIView):
    """Olympia tournament scoreboard view of a given account"""
    serializer_class = OlympiaScoreboardSerializer

    def get_object(self):
        return get_object_or_404(TournamentParticipant, address=self.kwargs['account_address'])
