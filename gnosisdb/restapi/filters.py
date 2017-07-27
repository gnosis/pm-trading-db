from django_filters import rest_framework as filters
from rest_framework.pagination import LimitOffsetPagination
from relationaldb.models import CentralizedOracle, UltimateOracle, Event, Market, Order, MarketShareEntry


class DefaultPagination(LimitOffsetPagination):
    max_limit = 50
    default_limit = 25


class CentralizedOracleFilter(filters.FilterSet):
    creator = filters.AllValuesMultipleFilter()
    creation_date = filters.DateTimeFromToRangeFilter()
    is_outcome_set = filters.BooleanFilter()
    owner = filters.AllValuesMultipleFilter()
    title = filters.CharFilter(name='event_description__title', lookup_expr='contains')
    description = filters.CharFilter(name='event_description__description', lookup_expr='contains')
    resolution_date = filters.DateTimeFromToRangeFilter(name='event_description__resolution_date')

    ordering = filters.OrderingFilter(
        fields=(
            ('creation_date', 'creation_date_order'),
            ('event_description__resolution_date', 'resolution_date_order')
        )
    )

    class Meta:
        model = CentralizedOracle
        fields = ('creator', 'creation_date', 'is_outcome_set', 'owner', 'title', 'description', 'ordering')


class UltimateOracleFilter(filters.FilterSet):
    creator = filters.AllValuesMultipleFilter()
    creation_date = filters.DateTimeFromToRangeFilter()
    is_outcome_set = filters.BooleanFilter()
    forwarded_oracle_creator = filters.AllValuesMultipleFilter(name='forwarded_oracle__creator')
    forwarded_oracle_creation_date = filters.DateTimeFromToRangeFilter(name='forwarded_oracle__creation_date')
    forwarded_oracle_is_outcome_set = filters.BooleanFilter(name='forwarded_oracle__is_outcome_set')
    forwarded_oracle_factory = filters.AllValuesMultipleFilter(name='forwarded_oracle__factory')

    ordering = filters.OrderingFilter(
        fields=(
            ('creation_date', 'creation_date_order'),
            ('forwarded_oracle__creation_date', 'forwarded_oracle_creation_date_order')
        )
    )

    class Meta:
        model = UltimateOracle
        fields = ('creator', 'creation_date', 'is_outcome_set', 'forwarded_oracle_creator',
                  'forwarded_oracle_creation_date', 'forwarded_oracle_is_outcome_set', 'forwarded_oracle_factory',
                  'ordering')


class EventFilter(filters.FilterSet):
    creator = filters.AllValuesMultipleFilter()
    creation_date = filters.DateTimeFromToRangeFilter()
    is_winning_outcome_set = filters.BooleanFilter()
    oracle_factory = filters.AllValuesMultipleFilter(name='oracle__factory')
    oracle_creator = filters.AllValuesMultipleFilter(name='oracle__creator')
    oracle_creation_date = filters.DateTimeFromToRangeFilter(name='oracle__creation_date')
    oracle_is_outcome_set = filters.BooleanFilter(name='oracle__is_outcome_set')

    ordering = filters.OrderingFilter(
        fields=(
            ('creation_date', 'creation_date_order'),
            ('oracle__creation_date', 'oracle_creation_date_order')
        )
    )

    class Meta:
        model = Event
        fields = ('creator', 'creation_date', 'is_winning_outcome_set', 'oracle_factory', 'oracle_creator',
                  'oracle_creation_date', 'oracle_is_outcome_set')


class MarketFilter(filters.FilterSet):
    creator = filters.AllValuesMultipleFilter()
    creation_date = filters.DateTimeFromToRangeFilter()
    market_maker = filters.AllValuesMultipleFilter()
    event_oracle_factory = filters.AllValuesMultipleFilter(name='event__oracle__factory')
    event_oracle_creator = filters.AllValuesMultipleFilter(name='event__oracle__creator')
    event_oracle_creation_date = filters.DateTimeFromToRangeFilter(name='event__oracle__creation_date')
    event_oracle_is_outcome_set = filters.BooleanFilter(name='event__oracle__is_outcome_set')

    ordering = filters.OrderingFilter(
        fields=(
            ('creation_date', 'creation_date_order'),
            ('event__oracle__creation_date', 'event_oracle_creation_date_order')
        )
    )

    class Meta:
        model = Market
        fields = ('creator', 'creation_date', 'market_maker', 'event_oracle_factory', 'event_oracle_creator',
                  'event_oracle_creation_date', 'event_oracle_is_outcome_set')


class MarketShareEntryFilter(filters.FilterSet):
    market = filters.AllValuesMultipleFilter()

    class Meta:
        model = MarketShareEntry
        fields = ('market',)
