from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from relationaldb.models import (
    ScalarEventDescription, CategoricalEventDescription, OutcomeTokenBalance, OutcomeToken,
    CentralizedOracle, UltimateOracle, Market, Order, ScalarEvent, CategoricalEvent
)
from gnosisdb.utils import remove_null_values, add_0x_prefix


class ContractSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        response = {
            'address': add_0x_prefix(instance.address),
            'factory_address': add_0x_prefix(instance.factory),
            'creator': add_0x_prefix(instance.creator),
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
    type = serializers.SerializerMethodField()

    class Meta:
        model = CentralizedOracle
        fields = ('contract', 'is_outcome_set', 'outcome', 'owner', 'event_description', 'type',)

    def get_type(self, obj):
        return 'CENTRALIZED'

    def to_representation(self, instance):
        # Prepend 0x prefix to owner
        instance.owner = add_0x_prefix(instance.owner)
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
    type = serializers.SerializerMethodField()

    class Meta:
        model = UltimateOracle
        fields = ('contract', 'is_outcome_set', 'outcome', 'collateral_token', 'spread_multiplier', 'challenge_period',
                  'challenge_amount', 'front_runner_period', 'forwarded_outcome', 'outcome_set_at_timestamp',
                  'front_runner', 'front_runner_set_at_timestamp', 'total_amount', 'forwarded_oracle', 'type',)

    def to_representation(self, instance):
        # Prepend 0x prefix to collateral_token
        instance.owner = add_0x_prefix(instance.collateral_token)
        response = super(UltimateOracleSerializer, self).to_representation(instance)
        return remove_null_values(response)

    def get_type(self, obj):
        return 'ULTIMATE'


class CategoricalEventSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(source='*', many=False, read_only=True)
    oracle = OracleSerializer()
    type = serializers.SerializerMethodField()
    class Meta:
        model = CategoricalEvent
        fields = ('contract', 'collateral_token', 'oracle', 'is_winning_outcome_set', 'outcome', 'type',)

    def get_type(self, obj):
        return 'CATEGORICAL'


class ScalarEventSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(source='*', many=False, read_only=True)
    oracle = OracleSerializer()
    type = serializers.SerializerMethodField()

    class Meta:
        model = ScalarEvent
        fields = ('contract', 'collateral_token', 'oracle', 'is_winning_outcome_set', 'outcome', 'lower_bound',
                  'upper_bound', 'type')

    def get_type(self, obj):
        return 'SCALAR'


class EventSerializer(serializers.Serializer):

    def to_representation(self, instance):
        result = None
        try:
            categorical_event = CategoricalEvent.objects.get(address=instance.address)
            result = CategoricalEventSerializer(categorical_event).to_representation(categorical_event)
            return remove_null_values(result)
        except CategoricalEvent.DoesNotExist:
            pass

        try:
            scalar_event = ScalarEvent.objects.get(address=instance.address)
            result = ScalarEventSerializer(scalar_event).to_representation(scalar_event)
            return remove_null_values(result)
        except ScalarEvent.DoesNotExist:
            pass


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

    def get_market_maker(self, obj):
        return add_0x_prefix(obj)


class MarketHistorySerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source="creation_date_time", read_only=True)
    net_outcome_tokens_sold = serializers.ListField(
        child=serializers.DecimalField(max_digits=80, decimal_places=0, read_only=True))

    class Meta:
        model = Order
        fields = ('date', 'net_outcome_tokens_sold')

    def to_representation(self, instance):
        response = super(MarketHistorySerializer, self).to_representation(instance)
        return remove_null_values(response)


class OutcomeTokenSerializer(serializers.ModelSerializer):
    totalSupply = serializers.DecimalField(source="total_supply", max_digits=80, decimal_places=0)
    class Meta:
        model = OutcomeToken
        fields = ('event', 'index', 'totalSupply', 'address')


class OutcomeTokenBalanceSerializer(serializers.ModelSerializer):

    outcomeToken = OutcomeTokenSerializer(source="outcome_token")

    class Meta:
        model = OutcomeTokenBalance
        fields = ('outcomeToken', 'owner', 'balance', )
