from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from relationaldb.models import EventDescription, ScalarEventDescription, CategoricalEventDescription, Oracle
from relationaldb.models import CentralizedOracle, UltimateOracle, Event, Market, MarketShareEntry
from gnosisdb.utils import remove_null_values


class ContractSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        response = {
            'address': instance.address,
            'factory_address': instance.factory,
            'creator': instance.creator,
            'creation_date': instance.creation_date_time,
            'creation_block': instance.creation_block
        }

        return remove_null_values(response)


class EventDescriptionSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        result = {
            'title': instance.title,
            'description': instance.description,
            'resolution_date': instance.resolution_date,
            'ipfs_hash': instance.ipfs_hash
        }

        try:
            scalar_event = ScalarEventDescription.objects.get(id=instance.id)
            result['unit'] = scalar_event.unit
            result['decimals'] = scalar_event.decimals
        except ObjectDoesNotExist:
            pass

        try:
            categorical_event = CategoricalEventDescription.objects.get(id=instance.id)
            result['outcomes'] = categorical_event.outcomes
        except ObjectDoesNotExist:
            pass

        return remove_null_values(result)


class OracleSerializer(serializers.Serializer):

    def to_representation(self, instance):
        result = None
        try:
            centralized_oracle = CentralizedOracle.objects.get(address=instance.address)
            result = CentralizedOracleSerializer(centralized_oracle).to_representation(centralized_oracle)
            return remove_null_values(result)
        except CentralizedOracle.DoesNotExist:
            pass

        try:
            ultimate_oracle = UltimateOracle.objects.get(address=instance.address)
            result = UltimateOracleSerializer(ultimate_oracle).to_representation(ultimate_oracle)
            return remove_null_values(result)
        except UltimateOracle.DoesNotExist:
            response = super(OracleSerializer, self).to_representation(instance)
            return remove_null_values(response)


class CentralizedOracleSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(source='*', many=False, read_only=True)
    is_outcome_set = serializers.BooleanField()
    outcome = serializers.IntegerField()
    owner = serializers.CharField(max_length=20)
    event_description = EventDescriptionSerializer(many=False, read_only=True)

    class Meta:
        model = CentralizedOracle
        fields = ('contract', 'is_outcome_set', 'outcome', 'owner', 'event_description')

    def to_representation(self, instance):
        response = super(CentralizedOracleSerializer, self).to_representation(instance)
        return remove_null_values(response)


class UltimateOracleSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(source='*', many=False, read_only=True)
    is_outcome_set = serializers.BooleanField()
    outcome = serializers.IntegerField()
    forwarded_oracle = OracleSerializer(many=False, read_only=True)
    collateral_token = serializers.CharField()
    spread_multiplier = serializers.IntegerField()
    challenge_period = serializers.IntegerField()
    challenge_amount = serializers.IntegerField()
    front_runner_period = serializers.IntegerField()
    forwarded_outcome = serializers.IntegerField()
    outcome_set_at_timestamp = serializers.IntegerField()
    front_runner = serializers.IntegerField()
    front_runner_set_at_timestamp = serializers.IntegerField()
    total_amount = serializers.IntegerField()

    class Meta:
        model = UltimateOracle
        fields = ('contract', 'is_outcome_set', 'outcome', 'collateral_token', 'spread_multiplier', 'challenge_period',
                  'challenge_amount', 'front_runner_period', 'forwarded_outcome', 'outcome_set_at_timestamp',
                  'front_runner', 'front_runner_set_at_timestamp', 'total_amount', 'forwarded_oracle')

    def to_representation(self, instance):
        response = super(UltimateOracleSerializer, self).to_representation(instance)
        return remove_null_values(response)


class OutcomeTokenSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance.address


class EventSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(source='*', many=False, read_only=True)
    collateral_token = serializers.CharField()
    oracle = OracleSerializer(many=False, read_only=True)
    is_winning_outcome_set = serializers.BooleanField()
    outcome = serializers.IntegerField()
    # outcome_tokens = OutcomeTokenSerializer(many=True, read_only=True)
    type = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('contract', 'collateral_token', 'oracle', 'is_winning_outcome_set', 'outcome', 'type',)

    def get_type(self, obj):
        if hasattr(obj, 'scalarevent'):
            return 'SCALAR'
        else:
            return 'CATEGORICAL'

    def to_representation(self, instance):
        response = super(EventSerializer, self).to_representation(instance)
        return remove_null_values(response)


class MarketSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(source='*', many=False, read_only=True)
    event = EventSerializer(many=False, read_only=True)
    market_maker = serializers.CharField()
    fee = serializers.IntegerField()
    funding = serializers.DecimalField(max_digits=80, decimal_places=0)
    net_outcome_tokens_sold = serializers.ListField(child=serializers.DecimalField(max_digits=80, decimal_places=0, read_only=True))
    stage = serializers.IntegerField()

    class Meta:
        model = Market
        fields = ('contract', 'event', 'market_maker', 'fee', 'funding', 'net_outcome_tokens_sold', 'stage')

    def to_representation(self, instance):
        response = super(MarketSerializer, self).to_representation(instance)
        return remove_null_values(response)


class MarketShareEntrySerializer(serializers.ModelSerializer):
    market = serializers.CharField(source='market__address')
    shares = serializers.ListField(source='net_outcome_tokens_owned',
                                   child=serializers.DecimalField(max_digits=80, decimal_places=0, read_only=True))

    class Meta:
        model = MarketShareEntry
        fields = ('market', 'shares')

    def to_representation(self, instance):
        response = super(MarketShareEntrySerializer, self).to_representation(instance)
        return remove_null_values(response)
