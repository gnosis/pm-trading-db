from datetime import timedelta

from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework.pagination import LimitOffsetPagination

from django_eth_events.utils import normalize_address_without_0x
from tradingdb.relationaldb.models import (CentralizedOracle, Event, Market,
                                           Order, OutcomeTokenBalance)


class DefaultPagination(LimitOffsetPagination):
    max_limit = 200
    default_limit = 100


class CentralizedOracleFilter(filters.FilterSet):
    creator = filters.AllValuesMultipleFilter()
    creation_date_time = filters.DateTimeFromToRangeFilter()
    is_outcome_set = filters.BooleanFilter()
    owner = filters.AllValuesMultipleFilter()
    title = filters.CharFilter(name='event_description__title', lookup_expr='contains')
    description = filters.CharFilter(name='event_description__description', lookup_expr='contains')
    resolution_date = filters.DateTimeFromToRangeFilter(name='event_description__resolution_date')

    ordering = filters.OrderingFilter(
        fields=(
            ('creation_date_time', 'creation_date_order'),
            ('event_description__resolution_date_time', 'resolution_date_order')
        )
    )

    class Meta:
        model = CentralizedOracle
        fields = ('creator', 'creation_date_time', 'is_outcome_set', 'owner', 'title', 'description', 'ordering')


class EventFilter(filters.FilterSet):
    creator = filters.AllValuesMultipleFilter()
    creation_date_time = filters.DateTimeFromToRangeFilter()
    is_winning_outcome_set = filters.BooleanFilter()
    oracle_factory = filters.AllValuesMultipleFilter(name='oracle__factory')
    oracle_creator = filters.AllValuesMultipleFilter(name='oracle__creator')
    oracle_creation_date_time = filters.DateTimeFromToRangeFilter(name='oracle__creation_date_time')
    oracle_is_outcome_set = filters.BooleanFilter(name='oracle__is_outcome_set')

    ordering = filters.OrderingFilter(
        fields=(
            ('creation_date_time', 'creation_date_order'),
            ('oracle__creation_date_time', 'oracle_creation_date_order')
        )
    )

    class Meta:
        model = Event
        fields = ('creator', 'creation_date_time', 'is_winning_outcome_set', 'oracle_factory', 'oracle_creator',
                  'oracle_creation_date_time', 'oracle_is_outcome_set')


class AddressInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class MarketFilter(filters.FilterSet):
    creator = filters.CharFilter(method='filter_creator')  # Accept multiple creators split by comma
    creation_date_time = filters.DateTimeFromToRangeFilter()
    market_maker = filters.AllValuesMultipleFilter()
    event_oracle_factory = filters.AllValuesMultipleFilter(name='event__oracle__factory')
    event_oracle_creator = filters.AllValuesMultipleFilter(name='event__oracle__creator')
    event_oracle_creation_date_time = filters.DateTimeFromToRangeFilter(name='event__oracle__creation_date_time')
    # TODO refactor, maybe duplicate resolution_date from event_description to market
    resolution_date_time = filters.DateTimeFromToRangeFilter(name='event__oracle__centralizedoracle__event_description__resolution_date')
    event_oracle_is_outcome_set = filters.BooleanFilter(name='event__oracle__is_outcome_set')
    collateral_token = filters.CharFilter(name='event__collateral_token', method='filter_collateral_token')

    ordering = filters.OrderingFilter(
        fields=(
            ('creation_date_time', 'creation_date_order'),
            ('event__oracle__creation_date_time', 'event_oracle_creation_date_order'),
            ('resolution_date_time', 'resolution_date_order'),
        )
    )

    class Meta:
        model = Market
        fields = ('creator', 'creation_date_time', 'market_maker', 'event_oracle_factory', 'event_oracle_creator',
                  'event_oracle_creation_date_time', 'event_oracle_is_outcome_set',
                  'resolution_date_time', 'collateral_token',)

    def filter_creator(self, queryset, name, value):
        creators = [normalize_address_without_0x(creator) for creator in value.split(',')]
        return queryset.filter(creator__in=creators)

    def filter_collateral_token(self, queryset, name, value):
        value = normalize_address_without_0x(value)
        return queryset.filter(event__collateral_token__iexact=value)


class MarketTradesFilter(filters.FilterSet):
    creation_date_time = filters.DateTimeFromToRangeFilter()
    collateral_token = filters.CharFilter(method='filter_collateral_token')

    ordering = filters.OrderingFilter(
        fields=(
            ('creation_date_time', 'creation_date_order'),
        )
    )

    class Meta:
        model = Order
        fields = ('creation_date_time', 'collateral_token',)

    def __init__(self, data=None, *args, **kwargs):
        # if filterset is bound, use initial values as defaults
        if data is not None and not 'creation_date_time_0' in data and not 'creation_date_time_1' in data:
            data = data.copy()
            data['creation_date_time_0'] = (timezone.now() - timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')
            data['creation_date_time_1'] = timezone.now()

        super().__init__(data, *args, **kwargs)

    def filter_collateral_token(self, queryset, name, value):
        value = normalize_address_without_0x(value)
        return queryset.filter(market__event__collateral_token__iexact=value)


class MarketSharesFilter(filters.FilterSet):
    creation_date_time = filters.DateTimeFromToRangeFilter()
    collateral_token = filters.CharFilter(method='filter_collateral_token')

    ordering = filters.OrderingFilter(
        fields=(
            ('creation_date_time', 'creation_date_order'),
        )
    )

    class Meta:
        model = OutcomeTokenBalance
        fields = ('creation_date_time', 'collateral_token',)

    def filter_collateral_token(self, queryset, name, value):
        value = normalize_address_without_0x(value)
        return queryset.filter(outcome_token__event__collateral_token__iexact=value)
