import sys
from datetime import datetime
from decimal import Decimal

from celery.utils.log import get_task_logger
from django.conf import settings
from ipfsapi.exceptions import ErrorResponse
from mpmath import mp
from rest_framework import serializers
from rest_framework.fields import CharField
from web3 import Web3

from chainevents.abis import abi_file_path, load_json_file
from django_eth_events.utils import normalize_address_without_0x
from django_eth_events.web3_service import Web3ServiceProvider
from gnosis.utils import calc_lmsr_marginal_price
from ipfs.ipfs import Ipfs

from . import models

# Ethereum addresses have 40 chars (without 0x)
ADDRESS_LENGTH = 40

mp.dps = 100
mp.pretty = True

logger = get_task_logger(__name__)


class BaseEventSerializer(serializers.BaseSerializer):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """
        Gets the kwargs passed to the serializer and produces a new data dictionary with:
            address: string
            creation_date_time: datetime
            creation_block: int

        In addition, all parameters contained in kwargs['data']['params'] are re-elaborated and added to
        the final data dictionary
        """
        if kwargs.get('block'):
            self.block = kwargs.pop('block')

        super().__init__(*args, **kwargs)

        self.initial_data = self.parse_event_data(kwargs.pop('data'))

    def parse_event_data(self, event_data):
        """
        Extract event_data and move event params moved to root object
        :param event_data: dictionary
        :return: dictionary with event params
        """

        return {param['name']: param['value'] for param in event_data.get('params')}


class ContractSerializer(BaseEventSerializer):
    """
    Serializes a Contract entity
    """
    class Meta:
        fields = ('address', )

    address = serializers.CharField(max_length=ADDRESS_LENGTH)

    def parse_event_data(self, event_data):
        """
        Move event params moved to root object
        :return: dictionary with event params moved to root object
        """

        parsed_event_data = super().parse_event_data(event_data)
        parsed_event_data.update({
            'address': event_data.get('address'),
        })
        return parsed_event_data


class BlockTimestampedSerializer(BaseEventSerializer):
    """
    Serializes the block informations
    """
    class Meta:
        fields = ('creation_date_time', 'creation_block', )

    creation_date_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    creation_block = serializers.IntegerField()

    def parse_event_data(self, event_data):
        parsed_event_data = super().parse_event_data(event_data)
        parsed_event_data.update({
            'creation_date_time': datetime.fromtimestamp(self.block.get('timestamp')),
            'creation_block': self.block.get('number'),
        })
        return parsed_event_data


class ContractSerializerTimestamped(ContractSerializer, BlockTimestampedSerializer):
    class Meta:
        fields = ContractSerializer.Meta.fields + BlockTimestampedSerializer.Meta.fields


class ContractCreatedByFactorySerializerTimestamped(ContractSerializer, BlockTimestampedSerializer):
    """
    Serializes a Contract Factory
    """
    class Meta:
        fields = ContractSerializer.Meta.fields + BlockTimestampedSerializer.Meta.fields + ('factory', 'creator')

    factory = serializers.CharField(max_length=ADDRESS_LENGTH)  # included prefix
    creator = serializers.CharField(max_length=ADDRESS_LENGTH)

    def parse_event_data(self, event_data):
        parsed_event_data = super().parse_event_data(event_data)
        parsed_event_data.update({
            'factory': event_data['address'],
        })
        return parsed_event_data


# ========================================================
#                 Custom Fields
# ========================================================
class IpfsHashField(CharField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_event_description(self, ipfs_hash):
        """Returns the IPFS event_description object"""
        return Ipfs().get(ipfs_hash)

    def to_internal_value(self, data):
        # Ipfs hash is returned as bytes
        data = data.decode() if isinstance(data, bytes) else data
        try:
            event_description = models.EventDescription.objects.get(ipfs_hash=data)
            if event_description.title is None:
                return self.get_event_description(data)
            else:
                return event_description
        except models.EventDescription.DoesNotExist:
            try:
                event_description_json = self.get_event_description(data)
            except Exception as e:
                raise serializers.ValidationError('IPFS hash must exist')

            if not isinstance(event_description_json, dict):
                raise serializers.ValidationError('Invalid json %s' % event_description_json)

            if not event_description_json.get('title'):
                raise serializers.ValidationError('Missing title field')

            if not event_description_json.get('resolutionDate'):
                raise serializers.ValidationError('Missing resolution date field')

            if not event_description_json.get('description'):
                raise serializers.ValidationError('Missing description field')

            if 'outcomes' in event_description_json and type(event_description_json['outcomes']) is list \
                    and len(event_description_json['outcomes']) > 1:
                categorical_json = {
                    'ipfs_hash': data,
                    'title': event_description_json['title'],
                    'description': event_description_json['description'],
                    'resolution_date': event_description_json['resolutionDate'],
                    'outcomes': event_description_json['outcomes']
                }
                # categorical
                event_description = models.CategoricalEventDescription.objects.create(**categorical_json)

            elif 'decimals' in event_description_json and 'unit' in event_description_json:
                scalar_json = {
                    'ipfs_hash': data,
                    'title': event_description_json['title'],
                    'description': event_description_json['description'],
                    'resolution_date': event_description_json['resolutionDate'],
                    'decimals': event_description_json['decimals'],
                    'unit': event_description_json['unit']
                }
                # scalar
                event_description = models.ScalarEventDescription.objects.create(**scalar_json)
            else:
                raise serializers.ValidationError('Event must be categorical or scalar')

            return event_description


class OracleField(CharField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        address_len = len(data)
        if address_len > ADDRESS_LENGTH:
            raise serializers.ValidationError('Maximum address length of {} chars, it has {}'.format(ADDRESS_LENGTH,
                                                                                                     address_len))
        elif address_len < ADDRESS_LENGTH:
            raise serializers.ValidationError('Maximum address length of {} chars, it has {}'.format(ADDRESS_LENGTH,
                                                                                                     address_len))
        else:
            # Check oracle exists or save Null
            try:
                oracle = models.Oracle.objects.get(address=data)
                return oracle
            except models.Oracle.DoesNotExist:
                raise serializers.ValidationError('Unknown Oracle address')


class EventField(CharField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            event = models.Event.objects.get(address=data)
            return event
        except models.Event.DoesNotExist:
            raise serializers.ValidationError('eventContract address must exist')


class OracleSerializerTimestamped(ContractCreatedByFactorySerializerTimestamped):
    """
    Serializes an Oracle
    """
    class Meta:
        fields = ContractCreatedByFactorySerializerTimestamped.Meta.fields + ('is_outcome_set', 'outcome')

    is_outcome_set = serializers.BooleanField(default=False)
    outcome = serializers.IntegerField(default=0)

    def rollback(self):
        pass


class CentralizedOracleSerializer(OracleSerializerTimestamped, serializers.ModelSerializer):
    """
    Serializes a Centralized Oracle
    """
    class Meta:
        model = models.CentralizedOracle
        fields = OracleSerializerTimestamped.Meta.fields + ('ipfsHash', 'centralizedOracle')

    centralizedOracle = serializers.CharField(max_length=ADDRESS_LENGTH, source='address')
    ipfsHash = IpfsHashField(source='event_description')

    def create(self, validated_data):
        validated_data['owner'] = validated_data['creator']
        validated_data['old_owner'] = validated_data['owner']
        return models.CentralizedOracle.objects.create(**validated_data)

    def rollback(self):
        self.instance.delete()


class EventSerializerTimestamped(ContractCreatedByFactorySerializerTimestamped, serializers.ModelSerializer):
    """
    Serializes an Event
    """
    class Meta:
        models = models.Event
        fields = ContractCreatedByFactorySerializerTimestamped.Meta.fields + ('collateralToken', 'creator', 'oracle',)

    collateralToken = serializers.CharField(max_length=ADDRESS_LENGTH, source='collateral_token')
    creator = serializers.CharField(max_length=ADDRESS_LENGTH)
    oracle = OracleField()


class ScalarEventSerializer(EventSerializerTimestamped, serializers.ModelSerializer):
    """
    Serializes a Scalar Event
    """
    class Meta:
        model = models.ScalarEvent
        fields = EventSerializerTimestamped.Meta.fields + ('lowerBound', 'upperBound', 'scalarEvent')

    lowerBound = serializers.IntegerField(source='lower_bound')
    upperBound = serializers.IntegerField(source='upper_bound')
    scalarEvent = serializers.CharField(source='address', max_length=ADDRESS_LENGTH)

    def validate(self, attrs):
        # Verify whether the attrs['oracle'] is a CentralizedOracle,
        # if so, check its event_description is a ScalarEventDescription
        attrs = super().validate(attrs=attrs)
        try:
            centralized_oracle = models.CentralizedOracle.objects.get(address=attrs['oracle'].address)
            models.ScalarEventDescription.objects.get(ipfs_hash=centralized_oracle.event_description.ipfs_hash)
        except models.ScalarEventDescription.DoesNotExist:
            raise serializers.ValidationError("Not existing ScalarEventDescription with oracle {}".format(attrs['oracle'].address))
        except models.CentralizedOracle.DoesNotExist:
            pass

        return attrs

    def rollback(self):
        self.instance.delete()


class CategoricalEventSerializer(EventSerializerTimestamped, serializers.ModelSerializer):
    """
    Serializes a Categorical Event
    """
    class Meta:
        model = models.CategoricalEvent
        fields = EventSerializerTimestamped.Meta.fields + ('categoricalEvent', 'outcomeCount',)

    categoricalEvent = serializers.CharField(source='address', max_length=ADDRESS_LENGTH)
    outcomeCount = serializers.IntegerField()

    def validate(self, attrs):
        # Verify whether attrs['oracle'] is a CentralizedOracle,
        # if so, check its event_description is a CategoricalEventDescription
        attrs = super().validate(attrs=attrs)
        try:
            centralized_oracle = models.CentralizedOracle.objects.get(address=attrs['oracle'].address)
            description = models.CategoricalEventDescription.objects.get(ipfs_hash=centralized_oracle.event_description.ipfs_hash)
            if len(description.outcomes) != attrs['outcomeCount']:
                raise serializers.ValidationError("Field outcomeCount does not match number of outcomes specified "
                                                  "in the event description.")
        except models.ScalarEventDescription.DoesNotExist:
            raise serializers.ValidationError(
                "Not existing CategoricalEventDescription with oracle {}".format(attrs['oracle'].address))
        except models.CentralizedOracle.DoesNotExist:
            pass

        return attrs

    def create(self, validated_data):
        del validated_data['outcomeCount']
        return super().create(validated_data)

    def rollback(self):
        self.instance.delete()


class MarketSerializerTimestamped(ContractCreatedByFactorySerializerTimestamped, serializers.ModelSerializer):
    """
    Serializes a Market
    """
    class Meta:
        model = models.Market
        fields = ContractCreatedByFactorySerializerTimestamped.Meta.fields + ('eventContract', 'marketMaker', 'fee',
                                                                   'market', 'revenue', 'collected_fees',)

    eventContract = EventField(source='event')
    marketMaker = serializers.CharField(max_length=ADDRESS_LENGTH, source='market_maker')
    fee = serializers.IntegerField()
    market = serializers.CharField(max_length=ADDRESS_LENGTH, source='address')
    revenue = serializers.IntegerField(default=0)
    collected_fees = serializers.IntegerField(default=0)

    def validate_marketMaker(self, market_maker_address):
        if not Web3.toChecksumAddress(settings.LMSR_MARKET_MAKER) == Web3.toChecksumAddress(market_maker_address):
            raise serializers.ValidationError('Market Maker {} does not exist'.format(market_maker_address))
        return market_maker_address

    def create(self, validated_data):
        # Check event type (Categorical or Scalar)
        try:
            categorical_event = models.CategoricalEvent.objects.get(address=validated_data.get('event').address)
            n_outcome_tokens = len(categorical_event.oracle.centralizedoracle.event_description.categoricaleventdescription.outcomes)
            net_outcome_tokens_sold = [0] * n_outcome_tokens
            marginal_prices = [str(1.0 / n_outcome_tokens) for _ in range(0, n_outcome_tokens)]
        except models.CategoricalEvent.DoesNotExist:
            scalar_event = models.ScalarEvent.objects.get(address=validated_data.get('event').address)
            # scalar, creating an array of size 2
            net_outcome_tokens_sold = [0, 0]
            marginal_prices = ['0.5', '0.5']

        validated_data.update(
            {
                'net_outcome_tokens_sold': net_outcome_tokens_sold,
                'marginal_prices': marginal_prices,
                'trading_volume': 0
            }
        )
        market = models.Market.objects.create(**validated_data)
        return market

    def rollback(self):
        self.instance.delete()


class ScalarEventDescriptionSerializer(serializers.ModelSerializer):
    """
    Serializes a Scalar Event Description
    """
    class Meta:
        model = models.ScalarEventDescription
        exclude = ('id',)


class CategoricalEventDescriptionSerializer(serializers.ModelSerializer):
    """
    Serializes a Categorical Event Description
    """
    class Meta:
        model = models.CategoricalEventDescription
        exclude = ('id',)


class IPFSEventDescriptionDeserializer(serializers.ModelSerializer):
    """
    Deserialize an IPFS object by passing its ipfs_hash
    """
    basic_fields = ('ipfs_hash', 'title', 'description', 'resolution_date',)
    scalar_fields = basic_fields + ('unit', 'decimals',)
    categorical_fields = basic_fields + ('outcomes',)

    class Meta:
        model = models.EventDescription
        fields = ('ipfs_hash',)

    def validate(self, data):
        try:
            json_obj = Ipfs().get(data['ipfs_hash'])
            json_obj['ipfs_hash'] = data['ipfs_hash']
        except ErrorResponse:
            raise serializers.ValidationError('IPFS Reference does not exist.')

        if 'title' not in json_obj:
            raise serializers.ValidationError('IPFS Object does not contain an event title.')
        elif 'description' not in json_obj:
            raise serializers.ValidationError('IPFS Object does not contain an event description.')
        elif 'resolution_date' not in json_obj:
            raise serializers.ValidationError('IPFS Object does not contain an event resolution date.')
        elif ('unit' not in json_obj or 'decimals' not in json_obj) and ('outcomes' not in json_obj):
            raise serializers.ValidationError('Event Description must be scalar, with both unit and decimals fields, '
                                              'or categorical, with an outcomes field.')
        elif ('unit' in json_obj and 'decimals' not in json_obj) or ('unit' not in json_obj and 'decimals' in json_obj):
            raise serializers.ValidationError('Scalar Event Description must have both unit and decimals fields.')
        elif 'unit' in json_obj and 'decimals' in json_obj and 'outcomes' in json_obj:
            raise serializers.ValidationError('Event description must be scalar or categorical, not both.')
        return json_obj

    def create(self, validated_data):
        if 'unit' in validated_data and 'decimals' in validated_data:
            fields = self.scalar_fields
            event_description_serializer = ScalarEventDescriptionSerializer
        elif 'outcomes' in validated_data:
            fields = self.categorical_fields
            event_description_serializer = CategoricalEventDescriptionSerializer
        else:
            # Should not be reachable if validate_ipfs_hash() is correct.
            raise serializers.ValidationError('Incomplete event description.')
        extracted = dict((key, validated_data[key]) for key in fields)
        instance = event_description_serializer(data=extracted)
        instance.is_valid(raise_exception=True)
        result = instance.save()
        return result


# ========================================================
#             Contract Instance serializers
# ========================================================

class OutcomeTokenInstanceSerializer(ContractSerializer, serializers.ModelSerializer):
    """
    Serializes an Outcome Token contract instance
    """
    class Meta:
        model = models.OutcomeToken
        fields = ContractSerializer.Meta.fields + ('address', 'index', 'outcomeToken',)

    address = EventField(source='event')
    outcomeToken = CharField(max_length=ADDRESS_LENGTH, source='address')
    index = serializers.IntegerField(min_value=0)

    def rollback(self):
        self.instance.delete()


class OutcomeTokenIssuanceSerializer(ContractSerializer, serializers.ModelSerializer):
    """
    Serializes the Outcome Token issuance event
    """
    class Meta:
        model = models.OutcomeToken
        fields = ('owner', 'amount', 'address',)

    owner = serializers.CharField(max_length=ADDRESS_LENGTH)
    amount = serializers.IntegerField()
    address = serializers.CharField(max_length=ADDRESS_LENGTH, source='outcome_token')

    def create(self, validated_data):
        # Creates or updates an outcome token balance for the given outcome_token.
        # Returns the outcome_token
        try:
            outcome_token_balance = models.OutcomeTokenBalance.objects.get(owner=validated_data.get('owner'),
                                                                           outcome_token__address=validated_data.get('outcome_token'))
            outcome_token_balance.balance += validated_data.get('amount')
            outcome_token_balance.outcome_token.total_supply += validated_data.get('amount')
            outcome_token_balance.outcome_token.save()
            outcome_token_balance.save()
            return outcome_token_balance.outcome_token
        except models.OutcomeTokenBalance.DoesNotExist:
            outcome_token = models.OutcomeToken.objects.get(address=validated_data.get('outcome_token'))
            outcome_token.total_supply += validated_data.get('amount')
            outcome_token.save()

            outcome_token_balance = models.OutcomeTokenBalance()
            outcome_token_balance.balance = validated_data.get('amount')
            outcome_token_balance.owner = validated_data.get('owner')
            outcome_token_balance.outcome_token = outcome_token
            outcome_token_balance.save()
            return outcome_token

    def rollback(self):
        try:
            outcome_token_balance = models.OutcomeTokenBalance.objects.get(
                owner=self.validated_data.get('owner'),
                outcome_token__address=self.validated_data.get('outcome_token')
            )
            outcome_token_balance.balance -= self.validated_data.get('amount')
            outcome_token_balance.save()
            self.instance.total_supply -= self.validated_data.get('amount')
            self.instance.save()
        except models.OutcomeTokenBalance.DoesNotExist:
            self.instance.total_supply -= self.validated_data.get('amount')
            self.instance.save()


class OutcomeTokenRevocationSerializer(ContractSerializer, serializers.ModelSerializer):
    """
    Serializes the Outcome Token revocation event
    """
    class Meta:
        model = models.OutcomeToken
        fields = ('owner', 'amount', 'address',)

    owner = serializers.CharField(max_length=ADDRESS_LENGTH)
    amount = serializers.IntegerField()
    address = serializers.CharField(max_length=ADDRESS_LENGTH, source='outcome_token')

    def validate(self, attrs):
        try:
            models.OutcomeTokenBalance.objects.get(owner=attrs.get('owner'),
                                                   outcome_token__address=attrs.get('outcome_token'))
            return attrs
        except models.OutcomeTokenBalance.DoesNotExist:
            raise serializers.ValidationError('OutcomeTokenBalance {} for owner {} doesn\'t exist'.format(
                attrs.get('outcome_token'),
                attrs.get('owner')
            ))

    def create(self, validated_data):
        outcome_token_balance = models.OutcomeTokenBalance.objects.get(owner=validated_data.get('owner'),
                                                                       outcome_token__address=validated_data.get('outcome_token'))
        outcome_token_balance.balance -= validated_data.get('amount')
        outcome_token_balance.outcome_token.total_supply -= validated_data.get('amount')
        # save the outcome_token
        outcome_token_balance.outcome_token.save()
        # save the outcome_token_balance
        outcome_token_balance.save()
        return outcome_token_balance.outcome_token

    def rollback(self):
        outcome_token_balance = models.OutcomeTokenBalance.objects.get(
            owner=self.validated_data.get('owner'),
            outcome_token__address=self.validated_data.get('outcome_token')
        )
        outcome_token_balance.balance += self.validated_data.get('amount')
        outcome_token_balance.save()
        self.instance.total_supply += self.validated_data.get('amount')
        self.instance.save()


class OutcomeAssignmentEventSerializer(ContractSerializer, serializers.ModelSerializer):
    """
    Serializes the OutcomeAssignment event
    """
    class Meta:
        model = models.Event
        fields = ('outcome', 'address',)

    outcome = serializers.IntegerField()
    address = serializers.CharField(max_length=ADDRESS_LENGTH)

    def create(self, validated_data):
        # Updates the event outcome
        event = None
        try:
            event = models.Event.objects.get(address=validated_data.get('address'))
            event.is_winning_outcome_set = True
            event.outcome = validated_data.get('outcome')
            event.save()
            return event
        except event.DoesNotExist:
            raise serializers.ValidationError('Event {} does not exist'.format(validated_data.get('address')))

    def rollback(self):
        self.instance.is_winning_outcome_set = False
        self.instance.outcome = None
        self.instance.save()


class OutcomeTokenTransferSerializer(ContractSerializer, serializers.ModelSerializer):
    """
    Serializes the Outcome Token transfer event
    """
    class Meta:
        model = models.OutcomeTokenBalance
        fields = ('from_address', 'to', 'value', 'address',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_data['from_address'] = self.initial_data.pop('from')

    value = serializers.IntegerField(min_value=0)
    address = serializers.CharField(max_length=ADDRESS_LENGTH, source="outcome_token")
    from_address = serializers.CharField(max_length=ADDRESS_LENGTH)
    to = serializers.CharField(max_length=ADDRESS_LENGTH)

    def create(self, validated_data):
        # Subtract balance from Outcome Token Balance
        from_balance = models.OutcomeTokenBalance.objects.get(owner=validated_data.get('from_address'),
                                                              outcome_token__address=validated_data.get('outcome_token'))
        from_balance.balance -= validated_data.get('value')
        from_balance.save()

        # Add balance to receiver
        try:
            to_balance = models.OutcomeTokenBalance.objects.get(owner=validated_data.get('to'),
                                                                outcome_token__address=validated_data.get('outcome_token'))
        except models.OutcomeTokenBalance.DoesNotExist:
            to_balance = models.OutcomeTokenBalance.objects.create(owner=validated_data.get('to'),
                                                                   outcome_token=from_balance.outcome_token)
        to_balance.balance += validated_data.get('value')
        to_balance.save()

        return to_balance

    def rollback(self):
        # got OutcomeTokenBalance by using 'From' property
        self.instance.balance += self.validated_data.get('value')
        self.instance.save()

        # Add balance to receiver
        try:
            to_balance = models.OutcomeTokenBalance.objects.get(
                owner=self.validated_data.get('to'),
                outcome_token__address=self.validated_data.get('outcome_token')
            )
        except models.OutcomeTokenBalance.DoesNotExist:
            to_balance = models.OutcomeTokenBalance.objects.create(
                owner=self.validated_data.get('to'),
                outcome_token=self.from_balance.outcome_token
            )

        if to_balance.balance - self.validated_data.get('value') == 0:
            to_balance.delete()
        else:
            to_balance.balance -= self.validated_data.get('value')
            to_balance.save()


class WinningsRedemptionSerializer(ContractSerializer, serializers.ModelSerializer):
    """
    Serializes the WinningsRedemption event
    """
    class Meta:
        model = models.Event
        fields = ('address', 'receiver', 'winnings',)

    address = serializers.CharField(max_length=ADDRESS_LENGTH)
    receiver = serializers.CharField(max_length=ADDRESS_LENGTH)
    winnings = serializers.IntegerField()

    def create(self, validated_data):
        # Sums the given winnings to the event redeemed_winnings
        try:
            event = models.Event.objects.get(address=validated_data.get('address'))
            event.redeemed_winnings += validated_data.get('winnings')
            event.save()
            return event
        except event.DoesNotExist:
            raise serializers.ValidationError('Event {} does not exist'.format(validated_data.get('address')))

    def rollback(self):
        self.instance.redeemed_winnings -= self.validated_data.get('winnings')
        self.instance.save()


class CentralizedOracleInstanceSerializer(CentralizedOracleSerializer):
    pass


class OwnerReplacementSerializer(ContractSerializer, serializers.ModelSerializer):
    """
    Serializes the Centralized Oracle OwnerReplacement event
    """
    class Meta:
        model = models.CentralizedOracle
        fields = ('address', 'newOwner',)

    address = serializers.CharField(max_length=ADDRESS_LENGTH)
    newOwner = serializers.CharField(max_length=ADDRESS_LENGTH)

    def create(self, validated_data):
        # Replaces the centralized oracle's owner if existing
        try:
            centralized_oracle = models.CentralizedOracle.objects.get(address=validated_data.get('address'))
            centralized_oracle.old_owner = centralized_oracle.owner
            centralized_oracle.owner = validated_data.get('newOwner')
            centralized_oracle.save()
            return centralized_oracle
        except models.CentralizedOracle.DoesNotExist:
            raise serializers.ValidationError('CentralizedOracle {} does not exist'.format(validated_data.get('address')))

    def rollback(self):
        self.instance.owner = self.instance.old_owner
        self.instance.save()
        return self.instance


class OutcomeAssignmentOracleSerializer(ContractSerializer, serializers.ModelSerializer):
    """
    Serializes the OutcomeAssignment Oracle event
    """
    class Meta:
        model = models.CentralizedOracle
        fields = ('address', 'outcome',)

    address = serializers.CharField(max_length=ADDRESS_LENGTH)
    outcome = serializers.IntegerField()

    def create(self, validated_data):
        # Updates the centralized_oracle outcome
        try:
            centralized_oracle = models.CentralizedOracle.objects.get(address=validated_data.get('address'))
            centralized_oracle.is_outcome_set = True
            centralized_oracle.outcome = validated_data.get('outcome')
            centralized_oracle.save()
            return centralized_oracle
        except centralized_oracle.DoesNotExist:
            raise serializers.ValidationError('CentralizedOracle {} does not exist'.format(validated_data.get('address')))

    def rollback(self):
        self.instance.is_outcome_set = False
        self.instance.outcome = None
        self.instance.save()
        return self.instance


class OutcomeTokenPurchaseSerializerTimestamped(ContractSerializerTimestamped, serializers.ModelSerializer):
    """
    Serializes the Market OutcomeTokenPurchase event
    """
    class Meta:
        model = models.BuyOrder
        fields = ContractSerializerTimestamped.Meta.fields + ('buyer', 'outcomeTokenIndex', 'outcomeTokenCount',
                                                         'outcomeTokenCost', 'marketFees',)

    address = serializers.CharField(max_length=ADDRESS_LENGTH)
    buyer = serializers.CharField(max_length=ADDRESS_LENGTH)
    outcomeTokenIndex = serializers.IntegerField()
    outcomeTokenCount = serializers.IntegerField()
    outcomeTokenCost = serializers.IntegerField()
    marketFees = serializers.IntegerField()

    def create(self, validated_data):
        try:
            market = models.Market.objects.get(address=validated_data.get('address'))
            token_index = validated_data.get('outcomeTokenIndex')
            token_count = validated_data.get('outcomeTokenCount')
            market.net_outcome_tokens_sold[token_index] += token_count
            market.collected_fees += validated_data.get('marketFees')

            outcome_token = market.event.outcome_tokens.get(index=token_index)

            # Create Order
            order = models.BuyOrder()
            order.creation_date_time = validated_data.get('creation_date_time')
            order.creation_block = validated_data.get('creation_block')
            order.market = market
            order.sender = validated_data.get('buyer')
            order.outcome_token = outcome_token
            order.outcome_token_count = token_count
            order.cost = validated_data.get('outcomeTokenCost') + validated_data.get('marketFees')
            order.outcome_token_cost = validated_data.get('outcomeTokenCost')
            order.fees = validated_data.get('marketFees')
            order.net_outcome_tokens_sold = market.net_outcome_tokens_sold

            # Calculate current marginal price
            order.marginal_prices = list(map(
                lambda index_: Decimal(calc_lmsr_marginal_price(int(index_[0]),
                                                                [int(x) for x in market.net_outcome_tokens_sold],
                                                                int(market.funding))
                                       ),
                enumerate(market.net_outcome_tokens_sold)
            ))

            # Save order successfully, save market changes, then save the share entry
            order.save()
            market.trading_volume += order.cost
            market.marginal_prices = order.marginal_prices
            market.save()
            return order
        except models.Market.DoesNotExist:
            raise serializers.ValidationError('Market with address {} does not exist.'.format(validated_data.get('address')))

    def rollback(self):
        token_index = self.validated_data.get('outcomeTokenIndex')
        token_count = self.validated_data.get('outcomeTokenCount')
        market = models.Market.objects.get(address=self.validated_data.get('address'))
        market.net_outcome_tokens_sold[token_index] -= token_count
        market.collected_fees -= self.validated_data.get('marketFees')
        market.trading_volume -= self.instance.cost
        market.marginal_prices = list(map(
            lambda index_: Decimal(calc_lmsr_marginal_price(int(index_[0]),
                                                            [int(x) for x in market.net_outcome_tokens_sold],
                                                            int(market.funding))
                                   ),
            enumerate(market.net_outcome_tokens_sold)
        ))

        # Remove order
        self.instance.delete()
        market.save()


class OutcomeTokenSaleSerializerTimestamped(ContractSerializerTimestamped, serializers.ModelSerializer):
    """
    Serializes the Market OutcomeTokenSale event
    """
    class Meta:
        model = models.SellOrder
        fields = ContractSerializerTimestamped.Meta.fields + ('seller', 'outcomeTokenIndex', 'outcomeTokenCount',
                                                              'outcomeTokenProfit', 'marketFees',)

    address = serializers.CharField(max_length=ADDRESS_LENGTH)
    seller = serializers.CharField(max_length=ADDRESS_LENGTH)
    outcomeTokenIndex = serializers.IntegerField()
    outcomeTokenCount = serializers.IntegerField()
    outcomeTokenProfit = serializers.IntegerField()
    marketFees = serializers.IntegerField()

    def create(self, validated_data):
        try:
            market = models.Market.objects.get(address=validated_data.get('address'))
            token_index = validated_data.get('outcomeTokenIndex')
            token_count = validated_data.get('outcomeTokenCount')
            market.net_outcome_tokens_sold[token_index] -= token_count
            market.collected_fees += validated_data.get('marketFees')

            # Get outcome token
            outcome_token = market.event.outcome_tokens.get(index=token_index)

            # Create Order
            order = models.SellOrder()
            order.creation_date_time = validated_data.get('creation_date_time')
            order.creation_block = validated_data.get('creation_block')
            order.market = market
            order.sender = validated_data.get('seller')
            order.outcome_token = outcome_token
            order.outcome_token_count = token_count
            order.profit = validated_data.get('outcomeTokenProfit') - validated_data.get('marketFees')
            order.outcome_token_profit = validated_data.get('outcomeTokenProfit')
            order.fees = validated_data.get('marketFees')
            order.net_outcome_tokens_sold = market.net_outcome_tokens_sold
            order.marginal_prices = list(map(
                lambda index_: Decimal(calc_lmsr_marginal_price(int(index_[0]),
                                                                [int(x) for x in market.net_outcome_tokens_sold],
                                                                int(market.funding))
                                       ),
                enumerate(market.net_outcome_tokens_sold)
            ))
            # Save order successfully, save market changes, then save the share entry
            order.save()
            market.marginal_prices = order.marginal_prices
            market.save()
            return order
        except models.Market.DoesNotExist:
            raise serializers.ValidationError('Market with address {} does not exist.' % validated_data.get('address'))

    def rollback(self):
        token_index = self.validated_data.get('outcomeTokenIndex')
        token_count = self.validated_data.get('outcomeTokenCount')
        market = models.Market.objects.get(address=self.validated_data.get('address'))
        market.net_outcome_tokens_sold[token_index] += token_count
        market.collected_fees -= self.validated_data.get('marketFees')

        market.marginal_prices = list(map(
            lambda index_: Decimal(calc_lmsr_marginal_price(int(index_[0]),
                                                            [int(x) for x in market.net_outcome_tokens_sold],
                                                            int(market.funding))
                                   ),
            enumerate(market.net_outcome_tokens_sold)
        ))

        # Remove order
        self.instance.delete()
        market.save()


class OutcomeTokenShortSaleOrderSerializerTimestamped(ContractSerializerTimestamped, serializers.ModelSerializer):
    """
    Serializes the Market OutcomeTokenShortSale event
    """
    class Meta:
        model = models.ShortSellOrder
        fields = ContractSerializerTimestamped.Meta.fields + ('buyer', 'outcomeTokenIndex', 'outcomeTokenCount', 'cost',)

    address = serializers.CharField(max_length=ADDRESS_LENGTH)
    buyer = serializers.CharField(max_length=ADDRESS_LENGTH)
    outcomeTokenIndex = serializers.IntegerField()
    outcomeTokenCount = serializers.IntegerField()
    cost = serializers.IntegerField()

    def create(self, validated_data):
        try:
            market = models.Market.objects.get(address=validated_data.get('address'))
            try:
                # get outcome token
                outcome_token = models.OutcomeToken.objects.get(index=validated_data.get('outcomeTokenIndex'))
                # Create Order
                order = models.ShortSellOrder()
                order.creation_date_time = validated_data.get('creation_date_time')
                order.creation_block = validated_data.get('creation_block')
                order.market = market
                order.sender = validated_data.get('buyer')
                # order.outcome_token_index = validated_data.get('outcomeTokenIndex')
                order.outcome_token = outcome_token
                order.outcome_token_count = validated_data.get('outcomeTokenCount')
                order.cost = validated_data.get('cost')
                order.net_outcome_tokens_sold = market.net_outcome_tokens_sold
                # Save order
                order.save()
                return order
            except models.OutcomeToken.DoesNotExist:
                raise serializers.ValidationError('OutcomeToken with index {} does not exist.' % validated_data.get('outcomeTokenIndex'))
        except models.Market.DoesNotExist:
            raise serializers.ValidationError('Market with address {} does not exist.' % validated_data.get('address'))

    def rollback(self):
        # Remove order
        self.instance.delete()


class MarketFundingSerializer(ContractSerializer, serializers.ModelSerializer):
    """
    Serializes the Market MarketFunding event
    """
    class Meta:
        model = models.Market
        fields = ('address', 'funding',)

    address = serializers.CharField(max_length=ADDRESS_LENGTH)
    funding = serializers.IntegerField()

    def create(self, validated_data):
        try:
            market = models.Market.objects.get(address=validated_data.get('address'))
            market.funding = validated_data.get('funding')
            market.stage = market.stages[1][0] # MarketFunded
            market.save()
            return market
        except models.Market.DoesNotExist:
            raise serializers.ValidationError('Market with address {} does not exist.' % validated_data.get('address'))

    def rollback(self):
        self.instance.funding = None
        self.instance.stage = self.instance.stages[0][0]  # Market created
        self.instance.save()
        return self.instance


class MarketClosingSerializer(ContractSerializer, serializers.ModelSerializer):
    """
    Serializes the Market MarketClosing event
    """
    class Meta:
        model = models.Market
        fields = ('address',)

    address = serializers.CharField(max_length=ADDRESS_LENGTH)

    def create(self, validated_data):
        try:
            market = models.Market.objects.get(address=validated_data.get('address'))
            market.stage = market.stages[2][0] # MarketClosed
            market.save()
            return market
        except models.Market.DoesNotExist:
            raise serializers.ValidationError('Market with address {} does not exist.' % validated_data.get('address'))

    def rollback(self):
        self.instance.stage = self.instance.stages[1][0] # Market funded
        self.instance.save()
        return self.instance


class FeeWithdrawalSerializer(ContractSerializer, serializers.ModelSerializer):
    """
    Serializes the Market FeeWithdrawal event
    """
    class Meta:
        model = models.Market
        fields = ('address', 'fees',)

    address = serializers.CharField(max_length=ADDRESS_LENGTH)
    fees = serializers.IntegerField()

    def create(self, validated_data):
        try:
            market = models.Market.objects.get(address=validated_data.get('address'))
            market.withdrawn_fees += validated_data.get('fees')
            market.save()
            return market
        except models.Market.DoesNotExist:
            raise serializers.ValidationError('Market with address {} does not exist.' % validated_data.get('address'))

    def rollback(self):
        self.instance.withdrawn_fees -= self.validated_data.get('fees')
        self.instance.save()
        return self.instance


class UportTournamentParticipantSerializerEventSerializerTimestamped(ContractSerializerTimestamped,
                                                                     serializers.ModelSerializer):
    """
    Serializes the Uport new Identitity event
    """
    class Meta:
        model = models.TournamentParticipant
        fields = ContractSerializerTimestamped.Meta.fields + ('identity',)

    identity = serializers.CharField(max_length=ADDRESS_LENGTH, source='address')
    # address = serializers.CharField(max_length=ADDRESS_LENGTH, source='factory')

    def validate_identity(self, identity_address):
        """
        Only not whitelisted users can be saved
        :param identity_address: a user participant address
        :return: validated identity address
        """
        whitelisted_users = models.TournamentWhitelistedCreator.objects.all().values_list('address', flat=True)
        if identity_address in whitelisted_users:
            raise serializers.ValidationError('Tournament participant {} is admin, wont be saved'.format(identity_address))
        else:
            return identity_address

    def create(self, validated_data):
        participants_amount = models.TournamentParticipant.objects.all().count()
        validated_data['current_rank'] = participants_amount + 1
        validated_data['past_rank'] = participants_amount + 1
        validated_data['diff_rank'] = 0
        validated_data.update({
            'address': normalize_address_without_0x(validated_data.get('address')),
        })

        participant = models.TournamentParticipant.objects.create(**validated_data)
        participant_balance = models.TournamentParticipantBalance()
        participant_balance.balance = 0
        participant_balance.participant = participant
        participant_balance.save()
        return participant

    def rollback(self):
        self.instance.delete()


class GenericTournamentParticipantEventSerializerTimestamped(ContractSerializerTimestamped, serializers.ModelSerializer):
    """
    Serializes the AddressRegistry AddressRegistration event
    event AddressRegistration(address registrant, address registeredMainnetAddress)
    """
    class Meta:
        model = models.TournamentParticipant
        fields = ContractSerializerTimestamped.Meta.fields + ('registrant', 'registeredMainnetAddress')

    registrant = serializers.CharField(max_length=ADDRESS_LENGTH, source='address')
    registeredMainnetAddress = serializers.CharField(max_length=ADDRESS_LENGTH, source='mainnet_address')

    def validate_registrant(self, registrant_address):
        if models.TournamentParticipant.objects.filter(address=registrant_address).exists():
            raise serializers.ValidationError('Duplicated registrant {} , wont be saved'.format(registrant_address))
        else:
            return registrant_address

    def validate_registeredMainnetAddress(self, identity_address):
        """
        Only not whitelisted users can be saved
        :param identity_address: a user participant address
        :return: validated identity address
        """
        whitelisted_users = models.TournamentWhitelistedCreator.objects.all().values_list('address', flat=True)
        if identity_address in whitelisted_users:
            raise serializers.ValidationError('Tournament participant {} is admin, wont be saved'.format(identity_address))
        else:
            return identity_address

    def create(self, validated_data):
        participants_amount = models.TournamentParticipant.objects.all().count()
        validated_data['current_rank'] = participants_amount + 1
        validated_data['past_rank'] = participants_amount + 1
        validated_data['diff_rank'] = 0
        validated_data.update({
            'address': normalize_address_without_0x(validated_data.get('address')),
            'mainnet_address': normalize_address_without_0x(validated_data.get('mainnet_address')),
        })

        participant = models.TournamentParticipant.objects.create(**validated_data)
        participant_balance = models.TournamentParticipantBalance()
        participant_balance.participant = participant
        try:
            # check blockchain balance
            web3_service = Web3ServiceProvider()
            web3 = web3_service.web3
            tournament_token_address = web3_service.make_sure_cheksumed_address(settings.TOURNAMENT_TOKEN)
            abi = load_json_file(abi_file_path('TournamentToken.json'))
            token_contract = web3.eth.contract(abi=abi, address=tournament_token_address)
            blockchain_balance = token_contract.functions.balanceOf(web3_service.make_sure_cheksumed_address(participant.address)).call()
            participant_balance.balance = blockchain_balance
        except:
            participant_balance.balance = 0
            logger.error('Could not get token balance for address %s, %s' % (participant.mainnet_address, sys.exc_info()))
        finally:
            participant_balance.save()

        return participant

    def rollback(self):
        self.instance.delete()


class TournamentTokenIssuanceSerializer(ContractSerializer, serializers.ModelSerializer):
    """
    Serializes the issuance of new Tournament Tokens
    """

    class Meta:
        model = models.TournamentParticipantBalance
        fields = ('owner', 'amount',)

    owner = serializers.CharField(max_length=ADDRESS_LENGTH)
    amount = serializers.IntegerField()

    def validate_owner(self, owner):
        try:
            models.TournamentParticipantBalance.objects.get(participant=owner)
        except models.TournamentParticipantBalance.DoesNotExist:
            raise serializers.ValidationError('Tournament Participant with address {} does not exist'.format(owner))
        return owner

    def create(self, validated_data):
        logger.info("issuance serializer")
        participant_balance, created = models.TournamentParticipantBalance.objects.get_or_create(
            participant=validated_data.get('owner')
        )
        participant_balance.balance += validated_data.get('amount')
        participant_balance.save()

        return participant_balance

    def rollback(self):
        self.instance.balance -= self.validated_data.get('amount')
        return self.instance.save()


class TournamentTokenTransferSerializer(ContractSerializer, serializers.ModelSerializer):
    """
    Serializes the token transfer event
    https://github.com/gnosis/gnosis-contracts/blob/master/contracts/Tokens/Token.sol#L11
    """

    class Meta:
        model = models.TournamentParticipantBalance
        fields = ('from_participant', 'to_participant', 'value',)

    from_participant = serializers.CharField(max_length=ADDRESS_LENGTH)
    to_participant = serializers.CharField(max_length=ADDRESS_LENGTH)
    value = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_data['from_participant'] = self.initial_data.pop('from')
        self.initial_data['to_participant'] = self.initial_data.pop('to')
        
    def validate(self, attrs):
        """
        One of the two participants could not be a Tournament participant, we need to check them
        and remove in case they're not a participant
        :return validated attrs
        :raise ValidationError
        """
        super().validate(attrs)
        error_message = ''
        try:
            models.TournamentParticipantBalance.objects.get(participant=attrs.get('from_participant'))
        except:
            error_message += 'Invalid from_participant: user with address {} does not exist. \n'.format(
                attrs.get('from_participant')
            )
            attrs.pop('from_participant')

        try:
            models.TournamentParticipantBalance.objects.get(participant=attrs.get('to_participant'))
        except:
            error_message += 'Invalid to_participant: user with address {} does not exist. \n'.format(
                attrs.get('from_participant')
            )
            attrs.pop('to_participant')

        if attrs.get('to_participant') is None and attrs.get('from_participant') is None:
            raise serializers.ValidationError(error_message)
        else:
            return attrs

    def create(self, validated_data):
        """
        :param validated_data:
        :return: TournamentParticipant istance
        """
        if validated_data.get('from_participant'):
            from_user = models.TournamentParticipantBalance.objects.get(participant=validated_data.get('from_participant'))
            from_user.balance -= validated_data.get('value')
            from_user.save()
            if validated_data.get('to_participant'):
                to_user = models.TournamentParticipantBalance.objects.get(participant=validated_data.get('to_participant'))
                to_user.balance += validated_data.get('value')
                to_user.save()
                return to_user
            else:
                return from_user
        else:
            to_user = models.TournamentParticipantBalance.objects.get(participant=validated_data.get('to_participant'))
            to_user.balance += validated_data.get('value')
            to_user.save()
            return to_user

    def rollback(self):
        """
        In order to reach the rollback method, one of the two participants must exist.
        See validate(attrs)
        :return: TournamentParticipant instance
        """
        if self.validated_data.get('from_participant'):
            from_user = models.TournamentParticipantBalance.objects.get(participant=self.validated_data.get('from_participant'))
            from_user.balance += self.validated_data.get('value')
            from_user.save()

            if self.validated_data.get('to_participant'):
                to_user = models.TournamentParticipantBalance.objects.get(participant=self.validated_data.get('to_participant'))
                to_user.balance -= self.validated_data.get('value')
                to_user.save()
                return to_user
            else:
                return from_user

        else:
            to_user = models.TournamentParticipantBalance.objects.get(participant=self.validated_data.get('to_participant'))
            to_user.balance -= self.validated_data.get('value')
            to_user.save()
            return to_user
