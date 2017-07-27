from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from relationaldb.models import (
    UltimateOracle, CentralizedOracle, Event, Market, MarketShareEntry, Order, OutcomeTokenBalance
)
from .serializers import (
    UltimateOracleSerializer, CentralizedOracleSerializer, EventSerializer, MarketSerializer,
    MarketShareEntrySerializer, MarketHistorySerializer, OutcomeTokenBalanceSerializer
)
from .filters import (
    CentralizedOracleFilter, UltimateOracleFilter, EventFilter, MarketFilter, DefaultPagination, MarketShareEntryFilter)

from datetime import datetime


class CentralizedOracleListView(generics.ListAPIView):
    queryset = CentralizedOracle.objects.all()
    serializer_class = CentralizedOracleSerializer
    filter_class = CentralizedOracleFilter
    pagination_class = DefaultPagination


class CentralizedOracleFetchView(generics.RetrieveAPIView):
    queryset = CentralizedOracle.objects.all()
    serializer_class = CentralizedOracleSerializer

    def get_object(self):
        return get_object_or_404(CentralizedOracle, address=self.kwargs['addr'])


class UltimateOracleListView(generics.ListAPIView):
    queryset = UltimateOracle.objects.all()
    serializer_class = UltimateOracleSerializer
    filter_class = UltimateOracleFilter
    pagination_class = DefaultPagination


class UltimateOracleFetchView(generics.RetrieveAPIView):
    queryset = UltimateOracle.objects.all()
    serializer_class = UltimateOracleSerializer

    def get_object(self):
        return get_object_or_404(UltimateOracle, address=self.kwargs['addr'])


class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_class = EventFilter
    pagination_class = DefaultPagination


class EventFetchView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_object(self):
        return get_object_or_404(Event, address=self.kwargs['addr'])


class MarketListView(generics.ListAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer
    filter_class = MarketFilter
    pagination_class = DefaultPagination


class MarketFetchView(generics.RetrieveAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer

    def get_object(self):
        return get_object_or_404(Market, address=self.kwargs['addr'])


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
    # filter_class = MarketShareEntryFilter

    def get_queryset(self):
        return OutcomeTokenBalance.objects.filter(
            owner = self.kwargs['addr'],
            outcome_token__address__in=list(
                Market.objects.get(
                    address=self.kwargs['market_address']
                ).event.outcometoken_set.values_list('address', flat=True)
            )
        )


class MarketHistoryView(generics.ListAPIView):
    """
    Returns the list of orders by providing the market address, as well as the 'From' and 'To'
    parameters referring the order creation date.
    """
    queryset = Order.objects.all()
    serializer_class = MarketHistorySerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        if 'market' in self.request.query_params and 'from' in self.request.query_params \
                and 'to' in self.request.query_params:
            return Order.objects.filter(market=self.request.query_params['market'], creation_date_time__gte=self.request.query_params['from'],
                                        creation_date_time__lte=self.request.query_params['to']).order_by('creation_date_time')
        elif 'market' in self.request.query_params and 'from' in self.request.query_params:
            return Order.objects.filter(market=self.request.query_params['market'], creation_date_time__gte=self.request.query_params['from']).order_by('creation_date_time')
        elif 'market':
            return Order.objects.filter(market = self.request.query_params['market']).order_by('creation_date_time')
        else:
            return None
