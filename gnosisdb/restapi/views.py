from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from gnosisdb.relationaldb.models import UltimateOracle, CentralizedOracle, Event, Market
from .serializers import UltimateOracleSerializer, CentralizedOracleSerializer, EventSerializer, MarketSerializer
from .filters import CentralizedOracleFilter, UltimateOracleFilter, EventFilter, MarketFilter


class CentralizedOracleListView(generics.ListAPIView):
    queryset = CentralizedOracle.objects.all()
    serializer_class = CentralizedOracleSerializer
    filter_class = CentralizedOracleFilter


class CentralizedOracleFetchView(generics.RetrieveAPIView):
    queryset = CentralizedOracle.objects.all()
    serializer_class = CentralizedOracleSerializer

    def get_object(self):
        return get_object_or_404(CentralizedOracle, address=self.kwargs['addr'])


class UltimateOracleListView(generics.ListAPIView):
    queryset = UltimateOracle.objects.all()
    serializer_class = UltimateOracleSerializer
    filter_class = UltimateOracleFilter


class UltimateOracleFetchView(generics.RetrieveAPIView):
    queryset = UltimateOracle.objects.all()
    serializer_class = UltimateOracleSerializer

    def get_object(self):
        return get_object_or_404(UltimateOracle, address=self.kwargs['addr'])


class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_class = EventFilter


class EventFetchView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_object(self):
        return get_object_or_404(Event, address=self.kwargs['addr'])


class MarketListView(generics.ListAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer
    filter_class = MarketFilter


class MarketFetchView(generics.RetrieveAPIView):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer

    def get_object(self):
        return get_object_or_404(Market, address=self.kwargs['addr'])


@api_view(['GET'])
def factories_view(request):
    # TODO Populate monitored factory addresses from django settings
    return Response()
