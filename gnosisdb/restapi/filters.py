from django_filters import rest_framework as filters
from gnosisdb.relationaldb.models import CentralizedOracle, UltimateOracle


class CentralizedOracleFilter(filters.FilterSet):
    creator = filters.AllValuesMultipleFilter()
    creation_date = filters.DateTimeFromToRangeFilter()
    is_outcome_set = filters.BooleanFilter()
    owner = filters.AllValuesMultipleFilter()
    title = filters.CharFilter(name='event_description__title', lookup_expr='contains')
    description = filters.CharFilter(name='event_description__description', lookup_expr='contains')
    resolution_date = filters.DateTimeFromToRangeFilter(name='event_description__resolution_date')

    class Meta:
        model = CentralizedOracle
        fields = ('creator', 'creation_date', 'is_outcome_set', 'owner', 'title', 'description')


class UltimateOracleFilter(filters.FilterSet):
    creator = filters.AllValuesMultipleFilter()
    creation_date = filters.DateTimeFromToRangeFilter()
    is_outcome_set = filters.BooleanFilter()
    forwarded_oracle_creator = filters.AllValuesMultipleFilter(name='forwarded_oracle__creator')
    forwarded_oracle_creation_date = filters.DateTimeFromToRangeFilter(name='forwarded_oracle__creation_date')
    forwarded_oracle_is_outcome_set = filters.BooleanFilter(name='forwarded_oracle__is_outcome_set')
    forwarded_oracle_factory = filters.AllValuesMultipleFilter(name='forwarded_oracle__factory_address')

    class Meta:
        model = UltimateOracle
        fields = ('creator', 'creation_date', 'is_outcome_set', 'forwarded_oracle_creator',
                  'forwarded_oracle_creation_date', 'forwarded_oracle_is_outcome_set', 'forwarded_oracle_factory')
