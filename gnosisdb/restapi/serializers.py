from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from relationaldb.models import (
    ScalarEventDescription, CategoricalEventDescription, OutcomeTokenBalance, OutcomeToken,
    CentralizedOracle, Market, Order, ScalarEvent, CategoricalEvent, BuyOrder, TournamentParticipant
)
from gnosisdb.utils import remove_null_values, add_0x_prefix, get_order_type, get_order_cost, get_order_profit
from django.db.models import Sum


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
        if isinstance(instance, ScalarEventDescription):
            scalar_event = instance
            result['unit'] = scalar_event.unit
            result['decimals'] = scalar_event.decimals
            return remove_null_values(result)
        elif isinstance(instance, CategoricalEventDescription):
            categorical_event = instance
            result['outcomes'] = categorical_event.outcomes
            return remove_null_values(result)
        try:
            scalar_event = instance.scalareventdescription
            result['unit'] = scalar_event.unit
            result['decimals'] = scalar_event.decimals
        except:
            categorical_event = instance.categoricaleventdescription
            result['outcomes'] = categorical_event.outcomes

        return remove_null_values(result)


class OracleSerializer(serializers.Serializer):

    def to_representation(self, instance):
        if isinstance(instance, CentralizedOracle):
            centralized_oracle = instance
        else:
            centralized_oracle = instance.centralizedoracle
        response = CentralizedOracleSerializer(centralized_oracle).to_representation(centralized_oracle)
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

    def get_owner(self, obj):
        return add_0x_prefix(obj)

    def get_type(self, obj):
        return 'CENTRALIZED'


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
        try:
            categorical_event = instance.categoricalevent
            result = CategoricalEventSerializer(categorical_event).to_representation(categorical_event)
            return remove_null_values(result)
        except:
            scalar_event = instance.scalarevent
            result = ScalarEventSerializer(scalar_event).to_representation(scalar_event)
            return remove_null_values(result)


class MarketSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(source='*', many=False, read_only=True)
    event = EventSerializer(many=False, read_only=True)
    market_maker = serializers.CharField()
    fee = serializers.IntegerField()
    funding = serializers.DecimalField(max_digits=80, decimal_places=0)
    net_outcome_tokens_sold = serializers.ListField(child=serializers.DecimalField(max_digits=80, decimal_places=0, read_only=True))
    stage = serializers.IntegerField()
    trading_volume = serializers.DecimalField(max_digits=80, decimal_places=0)
    withdrawn_fees = serializers.DecimalField(max_digits=80, decimal_places=0)
    collected_fees = serializers.DecimalField(max_digits=80, decimal_places=0)
    marginal_prices = serializers.ListField(child=serializers.DecimalField(max_digits=5, decimal_places=4))

    class Meta:
        model = Market
        fields = ('contract', 'event', 'market_maker', 'fee', 'funding', 'net_outcome_tokens_sold',
                  'stage', 'trading_volume', 'withdrawn_fees', 'collected_fees', 'marginal_prices',)

    def to_representation(self, instance):
        response = super(MarketSerializer, self).to_representation(instance)
        return remove_null_values(response)

    def get_market_maker(self, obj):
        return add_0x_prefix(obj)


class OutcomeTokenSerializer(serializers.ModelSerializer):
    totalSupply = serializers.DecimalField(source="total_supply", max_digits=80, decimal_places=0)
    class Meta:
        model = OutcomeToken
        fields = ('event', 'index', 'totalSupply', 'address')


class MarketTradesSerializer(serializers.ModelSerializer):
    """Serializes the list of orders (trades) for the given market"""
    date = serializers.DateTimeField(source="creation_date_time", read_only=True)
    net_outcome_tokens_sold = serializers.ListField(
        child=serializers.DecimalField(max_digits=80, decimal_places=0, read_only=True)
    )
    marginal_prices = serializers.ListField(child=serializers.DecimalField(max_digits=5, decimal_places=4))
    outcome_token = OutcomeTokenSerializer()
    outcome_token_count = serializers.DecimalField(max_digits=80, decimal_places=0)
    order_type = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    event_description = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('date', 'net_outcome_tokens_sold', 'marginal_prices', 'outcome_token',
                  'outcome_token_count', 'order_type', 'cost', 'profit', 'event_description', 'owner', )

    def get_order_type(self, obj):
        return get_order_type(obj)

    def get_cost(self, obj):
        return str(get_order_cost(obj))

    def get_profit(self, obj):
        return str(get_order_profit(obj))

    def get_event_description(self, obj):
        try:
            obj.outcome_token.event.oracle.centralizedoracle
            event_description = obj.outcome_token.event.oracle.centralizedoracle.event_description
            result = EventDescriptionSerializer(event_description).to_representation(event_description)
            return result
        except CentralizedOracle.DoesNotExist:
            return {}

    def get_owner(self, obj):
        return add_0x_prefix(obj.sender)

    def to_representation(self, instance):
        response = super(MarketTradesSerializer, self).to_representation(instance)
        return remove_null_values(response)


class MarketParticipantTradesSerializer(serializers.ModelSerializer):
    """Serializes the list of orders (trades) for the given sender address and market"""
    date = serializers.DateTimeField(source="creation_date_time", read_only=True)
    # net_outcome_tokens_sold = serializers.ListField(
    #     child=serializers.DecimalField(max_digits=80, decimal_places=0, read_only=True))
    outcome_token = OutcomeTokenSerializer()
    outcome_token_count = serializers.DecimalField(max_digits=80, decimal_places=0)
    market = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    order_type = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    marginal_prices = serializers.ListField(child=serializers.DecimalField(max_digits=5, decimal_places=4))

    class Meta:
        model = Order
        fields = ('date', 'outcome_token', 'outcome_token_count', 'market', 'owner', 'order_type', 'profit', 'cost', 'marginal_prices', )

    def get_market(self, obj):
        return add_0x_prefix(obj.market.address)

    def get_owner(self, obj):
        return add_0x_prefix(obj.sender)

    def get_order_type(self, obj):
        return get_order_type(obj)

    def get_cost(self, obj):
        return str(get_order_cost(obj))

    def get_profit(self, obj):
        return str(get_order_profit(obj))

    def to_representation(self, instance):
        response = super(MarketParticipantTradesSerializer, self).to_representation(instance)
        return remove_null_values(response)


class OutcomeTokenBalanceSerializer(serializers.ModelSerializer):

    outcome_token = OutcomeTokenSerializer()
    event_description = serializers.SerializerMethodField()
    marginal_price = serializers.SerializerMethodField()

    class Meta:
        model = OutcomeTokenBalance
        fields = ('outcome_token', 'owner', 'balance', 'event_description', 'marginal_price', )

    def get_event_description(self, obj):
        try:
            event_description = obj.outcome_token.event.oracle.centralizedoracle.event_description
            result = EventDescriptionSerializer(event_description).to_representation(event_description)
            return result
        except CentralizedOracle.DoesNotExist:
            return {}

    def get_marginal_price(self, obj):
        return obj.outcome_token.event.markets.all()[0].marginal_prices[obj.outcome_token.index]


class OlympiaScoreboardSerializer(serializers.ModelSerializer):
    """Serializes an olympia tournament participant"""
    class Meta:
        model = TournamentParticipant
        fields = ('account', 'balance', 'contract', 'current_rank', 'past_rank', 'diff_rank', 'score', 'predicted_profit', 'predictions',)

    contract = ContractSerializer(source='*', many=False, read_only=True)
    account = serializers.SerializerMethodField()
    balance = serializers.DecimalField(max_digits=80, decimal_places=0, source='tournament_balance.balance')

    def get_account(self, obj):
        return add_0x_prefix(obj.address)

