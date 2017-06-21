from rest_framework import serializers
from rest_framework.fields import CharField
from relationaldb import models
from ipfs.ipfs import Ipfs
from datetime import datetime
from ipfsapi.exceptions import ErrorResponse
from time import mktime
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


class BlockTimestampedSerializer(serializers.BaseSerializer):
    class Meta:
        fields = ('creation_date_time', 'creation_block', )

    creation_date_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    creation_block = serializers.IntegerField()


class ContractEventTimestamped(BlockTimestampedSerializer):
    class Meta:
        fields = BlockTimestampedSerializer.Meta.fields + ('address',)

    address = serializers.CharField(max_length=40)

    def __init__(self, *args, **kwargs):
        self.block = kwargs.pop('block')
        super(ContractEventTimestamped, self).__init__(*args, **kwargs)
        data = kwargs.pop('data')
        # Event params moved to root object
        new_data = {
            'address': data.get('address'),
            'creation_date_time': datetime.fromtimestamp(self.block.get('timestamp')),
            'creation_block': self.block.get('number')
        }

        for param in data.get('params'):
            new_data[param[u'name']] = param[u'value']

        self.initial_data = new_data


# Declare basic fields, join params on root object and
class ContractSerializer(serializers.BaseSerializer):
    class Meta:
        fields = ('address', )

    address = serializers.CharField(max_length=40)


class ContractCreatedByFactorySerializer(BlockTimestampedSerializer, ContractSerializer):
    class Meta:
        fields = BlockTimestampedSerializer.Meta.fields + ContractSerializer.Meta.fields + ('factory', 'creator')

    factory = serializers.CharField(max_length=40)  # included prefix
    creator = serializers.CharField(max_length=40)

    def __init__(self, *args, **kwargs):
        self.block = kwargs.pop('block')
        super(ContractCreatedByFactorySerializer, self).__init__(*args, **kwargs)
        data = kwargs.pop('data')
        # Event params moved to root object
        new_data = {
            'address': data[u'address'], # TODO comment this with Denis
            'factory': data[u'address'],
            'creation_date_time': datetime.fromtimestamp(self.block.get('timestamp')),
            'creation_block': self.block.get('number')
        }

        for param in data.get('params'):
            new_data[param[u'name']] = param[u'value']

        self.initial_data = new_data


class ContractNotTimestampted(ContractSerializer):
    class Meta:
        fields = ContractSerializer.Meta.fields

    def __init__(self, *args, **kwargs):
        if kwargs.get('block'):
            self.block = kwargs.pop('block')
        super(ContractNotTimestampted, self).__init__(*args, **kwargs)
        data = kwargs.pop('data')
        # Event params moved to root object
        new_data = {
            'address': data.get('address')
        }

        for param in data.get('params'):
            new_data[param[u'name']] = param[u'value']

        self.initial_data = new_data



class IpfsHashField(CharField):

    def __init__(self, **kwargs):
        super(IpfsHashField, self).__init__(**kwargs)

    def get_event_description(self, ipfs_hash):
        """Returns the IPFS event_description object"""
        ipfs = Ipfs()
        return ipfs.get(ipfs_hash)

    def to_internal_value(self, data):
        event_description = None
        event_description_json = None
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

            # add ipfs_hash to description_json
            event_description_json.update({'ipfs_hash': data})

            if 'outcomes' in event_description_json:
                # categorical
                event_description = models.CategoricalEventDescription.objects.create(**event_description_json)

            elif 'decimals' in event_description_json and 'unit' in event_description_json:
                # scalar
                event_description = models.ScalarEventDescription.objects.create(**event_description_json)
            else:
                raise serializers.ValidationError('Event must be categorical or scalar')

            return event_description


class OracleField(CharField):
    def __init__(self, **kwargs):
        super(OracleField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        address_len = len(data)
        if address_len > 40:
            raise serializers.ValidationError('Maximum address length of 40 chars')
        elif address_len < 40:
            raise serializers.ValidationError('Address must have 40 chars')
        else:
            # Check oracle exists or save Null
            try:
                oracle = models.Oracle.objects.get(address=data)
                return oracle
            except models.Oracle.DoesNotExist:
                return None


class EventField(CharField):
    def __init__(self, **kwargs):
        super(EventField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        event = None
        try:
            event = models.Event.objects.get(address=data)
            return event
        except models.Event.DoesNotExist:
            raise serializers.ValidationError('eventContract address must exist')


class OracleSerializer(ContractCreatedByFactorySerializer):
    class Meta:
        fields = ContractCreatedByFactorySerializer.Meta.fields + ('is_outcome_set', 'outcome')

    is_outcome_set = serializers.BooleanField(default=False)
    outcome = serializers.IntegerField(default=0)


class CentralizedOracleSerializer(OracleSerializer, serializers.ModelSerializer):

    class Meta:
        model = models.CentralizedOracle
        fields = OracleSerializer.Meta.fields + ('ipfsHash', 'centralizedOracle')

    centralizedOracle = serializers.CharField(max_length=40, source='address')
    ipfsHash = IpfsHashField(source='event_description')

    def create(self, validated_data):
        validated_data['owner'] = validated_data['creator']
        return models.CentralizedOracle.objects.create(**validated_data)


class UltimateOracleSerializer(OracleSerializer, serializers.ModelSerializer):

    class Meta:
        model = models.UltimateOracle
        fields = OracleSerializer.Meta.fields + ('ultimateOracle', 'oracle', 'collateralToken',
                                                 'spreadMultiplier', 'challengePeriod', 'challengeAmount',
                                                 'frontRunnerPeriod')
    ultimateOracle = serializers.CharField(max_length=40, source='address')
    oracle = OracleField(source='forwarded_oracle')
    collateralToken = serializers.CharField(max_length=40, source='collateral_token')
    spreadMultiplier = serializers.IntegerField(source='spread_multiplier')
    challengePeriod = serializers.IntegerField(source='challenge_period')
    challengeAmount = serializers.IntegerField(source='challenge_amount')
    frontRunnerPeriod = serializers.IntegerField(source='front_runner_period')


class EventSerializer(ContractCreatedByFactorySerializer, serializers.ModelSerializer):

    class Meta:
        models = models.Event
        fields = ContractCreatedByFactorySerializer.Meta.fields + ('collateralToken', 'creator', 'oracle',)

    collateralToken = serializers.CharField(max_length=40, source='collateral_token')
    creator = serializers.CharField(max_length=40)
    oracle = OracleField()


class ScalarEventSerializer(EventSerializer, serializers.ModelSerializer):

    class Meta:
        model = models.ScalarEvent
        fields = EventSerializer.Meta.fields + ('lowerBound', 'upperBound', 'scalarEvent')

    lowerBound = serializers.IntegerField(source='lower_bound')
    upperBound = serializers.IntegerField(source='upper_bound')
    scalarEvent = serializers.CharField(source='address', max_length=40)


class CategoricalEventSerializer(EventSerializer, serializers.ModelSerializer):
    class Meta:
        model = models.CategoricalEvent
        fields = EventSerializer.Meta.fields + ('categoricalEvent',)

    categoricalEvent = serializers.CharField(source='address', max_length=40)


class MarketSerializer(ContractCreatedByFactorySerializer, serializers.ModelSerializer):

    class Meta:
        model = models.Market
        fields = ContractCreatedByFactorySerializer.Meta.fields + ('eventContract', 'marketMaker', 'fee',
                                                                   'market', 'revenue', 'collected_fees',)

    eventContract = EventField(source='event')
    marketMaker = serializers.CharField(max_length=40, source='market_maker')
    fee = serializers.IntegerField()
    market = serializers.CharField(max_length=40, source='address')
    revenue = serializers.IntegerField(default=0)
    collected_fees = serializers.IntegerField(default=0)


class ScalarEventDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ScalarEventDescription
        exclude = ('id',)


class CategoricalEventDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CategoricalEventDescription
        exclude = ('id',)


class IPFSEventDescriptionDeserializer(serializers.ModelSerializer):
    basic_fields = ('ipfs_hash', 'title', 'description', 'resolution_date',)
    scalar_fields = basic_fields + ('unit', 'decimals',)
    categorical_fields = basic_fields + ('outcomes',)

    class Meta:
        model = models.EventDescription
        fields = ('ipfs_hash',)

    def validate(self, data):
        json_obj = None
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
            Serializer = ScalarEventDescriptionSerializer
        elif 'outcomes' in validated_data:
            fields = self.categorical_fields
            Serializer = CategoricalEventDescriptionSerializer
        else:
            # Should not be reachable if validate_ipfs_hash() is correct.
            raise serializers.ValidationError('Incomplete event description.')
        extracted = dict((key, validated_data[key]) for key in fields)
        instance = Serializer(data=extracted)
        instance.is_valid(raise_exception=True)
        result = instance.save()
        return result


# Instance Serializers

class OutcomeTokenInstanceSerializer(ContractNotTimestampted, serializers.ModelSerializer):
    class Meta:
        model = models.OutcomeToken
        fields = ContractSerializer.Meta.fields + ('address', 'index', 'outcomeToken',)

    address = EventField(source='event')
    outcomeToken = CharField(max_length=40, source='address')
    index = serializers.IntegerField(min_value=0)


class OutcomeTokenIssuanceSerializer(ContractNotTimestampted, serializers.ModelSerializer):

    class Meta:
        model = models.OutcomeToken
        fields = ('owner', 'amount', 'address',)

    owner = serializers.CharField(max_length=40)
    amount = serializers.IntegerField()
    address = serializers.CharField(max_length=40, source='outcome_token')

    def create(self, validated_data):
        logger.info('++++++++++++++++++> {}'.format(validated_data))
        outcome_token = None
        outcome_token_balance = None
        try:
            outcome_token_balance = models.OutcomeTokenBalance.objects.get(owner=validated_data['owner'],
                                                                           outcome_token__address=validated_data['outcome_token'])
            outcome_token_balance.balance += validated_data['amount']
            outcome_token_balance.outcome_token.total_supply += validated_data['amount']
            outcome_token_balance.outcome_token.save()
            outcome_token_balance.save()
            logger.info('Increased issuance : {}'.format(outcome_token_balance.outcome_token.total_supply))
            logger.info('Outcome token Owner : {}'.format(outcome_token_balance.owner))
            return outcome_token_balance.outcome_token
        except models.OutcomeTokenBalance.DoesNotExist:
            outcome_token = models.OutcomeToken.objects.get(address=validated_data['outcome_token'])
            outcome_token.total_supply += validated_data['amount']
            outcome_token.save()

            outcome_token_balance = models.OutcomeTokenBalance()
            outcome_token_balance.balance = validated_data['amount']
            outcome_token_balance.owner = validated_data['owner']
            outcome_token_balance.outcome_token = outcome_token
            outcome_token_balance.save()

            logger.info('Created issuance issuance : {}'.format(outcome_token_balance.outcome_token.total_supply))
            logger.info('Outcome token Owner : {}'.format(outcome_token_balance.owner))

            return outcome_token


class OutcomeTokenRevocationSerializer(ContractNotTimestampted, serializers.ModelSerializer):

    class Meta:
        model = models.OutcomeToken
        fields = ('owner', 'amount', 'address',)

    owner = serializers.CharField(max_length=40)
    amount = serializers.IntegerField()
    address = serializers.CharField(max_length=40, source='outcome_token')

    def create(self, validated_data):
        outcome_token = None
        outcome_token_balance = None
        try:
            outcome_token_balance = models.OutcomeTokenBalance.objects.get(owner=validated_data.get('owner'))
            outcome_token_balance.balance -= validated_data.get('amount')
            outcome_token_balance.outcome_token.total_supply -= validated_data.get('amount')
            # TODO check if exists a better solution to automatically update related models
            outcome_token_balance.outcome_token.save()
            outcome_token_balance.save()
        except models.OutcomeTokenBalance.DoesNotExist:
            pass

        return outcome_token_balance.outcome_token


class OutcomeAssignmentEventSerializer(ContractNotTimestampted, serializers.ModelSerializer):

    class Meta:
        model = models.Event
        fields = ('outcome', 'address',)

    outcome = serializers.IntegerField()
    address = serializers.CharField(max_length=40)

    def create(self, validated_data):
        event = None
        try:
            event = models.Event.objects.get(address=validated_data.get('address'))
            event.is_winning_outcome_set = True
            event.outcome = validated_data.get('outcome')
            event.save()
            return event
        except event.DoesNotExist:
            raise serializers.ValidationError('Event %s does not exist'.format(validated_data.get('address')))


class OutcomeTokenTransferSerializer(ContractNotTimestampted, serializers.ModelSerializer):

    class Meta:
        model = models.OutcomeTokenBalance
        fields = ('from_address', 'to', 'value', 'address',)

    def __init__(self, *args, **kwargs):
        super(OutcomeTokenTransferSerializer, self).__init__(*args, **kwargs)
        self.initial_data['from_address'] = self.initial_data.pop('from')

    value = serializers.IntegerField(min_value=0)
    address = serializers.CharField(max_length=40, source="outcome_token")
    from_address = serializers.CharField(max_length=40)
    to = serializers.CharField(max_length=40)

    def create(self, validated_data):
        # Substract balance from Outcome Token Balance
        from_balance = models.OutcomeTokenBalance.objects.get(owner=validated_data['from_address'],
                                                              outcome_token__address=validated_data['outcome_token'])
        from_balance.balance -= validated_data['value']
        from_balance.save()

        # Add balance to receiver
        to_balance = None
        try:
            to_balance = models.OutcomeTokenBalance.objects.get(owner=validated_data['to'],
                                                                outcome_token__address=validated_data['outcome_token'])
        except models.OutcomeTokenBalance.DoesNotExist:
            to_balance = models.OutcomeTokenBalance.objects.create(owner=validated_data['to'],
                                                                   outcome_token=from_balance.outcome_token)
        to_balance.balance += validated_data['value']
        to_balance.save()

        return to_balance


class WinningsRedemptionSerializer(ContractNotTimestampted, serializers.ModelSerializer):

    class Meta:
        model = models.Event
        fields = ('address', 'receiver', 'winnings',)

    address = serializers.CharField(max_length=40)
    receiver = serializers.CharField(max_length=40)
    winnings = serializers.IntegerField()

    def create(self, validated_data):
        event = None
        try:
            event = models.Event.objects.get(address=validated_data.get('address'))
            event.redeemed_winnings += validated_data.get('winnings')
            event.save()
            return event
        except event.DoesNotExist:
            raise serializers.ValidationError('Event %s does not exist'.format(validated_data.get('address')))


class CentralizedOracleInstanceSerializer(CentralizedOracleSerializer):
    pass


class OwnerReplacementSerializer(ContractNotTimestampted, serializers.ModelSerializer):

    class Meta:
        model = models.CentralizedOracle
        fields = ('address', 'newOwner',)

    address = serializers.CharField(max_length=40)
    newOwner = serializers.CharField(max_length=40)

    def create(self, validated_data):
        centralized_oracle = None
        try:
            centralized_oracle = models.CentralizedOracle.objects.get(address=validated_data.get('address'))
            centralized_oracle.owner = validated_data.get('newOwner')
            centralized_oracle.save()
            return centralized_oracle
        except models.CentralizedOracle.DoesNotExist:
            raise serializers.ValidationError('CentralizedOracle %s does not exist'.format(validated_data.get('address')))


class OutcomeAssignmentOracleSerializer(ContractNotTimestampted, serializers.ModelSerializer):

    class Meta:
        model = models.CentralizedOracle
        fields = ('address', 'outcome',)

    address = serializers.CharField(max_length=40)
    outcome = serializers.IntegerField()

    def create(self, validated_data):
        centralized_oracle = None
        try:
            centralized_oracle = models.CentralizedOracle.objects.get(address=validated_data.get('address'))
            centralized_oracle.is_outcome_set = True
            centralized_oracle.outcome = validated_data.get('outcome')
            centralized_oracle.save()
            return centralized_oracle
        except centralized_oracle.DoesNotExist:
            raise serializers.ValidationError('CentralizedOracle %s does not exist'.format(validated_data.get('address')))


class ForwardedOracleOutcomeAssignmentSerializer(ContractNotTimestampted, serializers.ModelSerializer):

    class Meta:
        model = models.UltimateOracle
        fields = ('address', 'outcome',)

    address = serializers.CharField(max_length=40)
    outcome = serializers.IntegerField()

    def create(self, validated_data):
        ultimate_oracle = None
        try:
            ultimate_oracle = models.UltimateOracle.objects.get(address=validated_data.get('address'))
            ultimate_oracle.outcome_set_at_timestamp = mktime(datetime.now().timetuple())
            ultimate_oracle.save()
            if not ultimate_oracle.forwarded_oracle.is_outcome_set:
                ultimate_oracle.forwarded_oracle.is_outcome_set = True
                ultimate_oracle.forwarded_oracle.outcome = validated_data.get('outcome')
                ultimate_oracle.forwarded_oracle.save()
            return ultimate_oracle
        except models.UltimateOracle.DoesNotExist:
            raise serializers.ValidationError('UltimateOracle %s does not exist'.format(validated_data.get('address')))


class OutcomeChallengeSerializer(ContractNotTimestampted, serializers.ModelSerializer):

    class Meta:
        model = models.UltimateOracle
        fields = ('address', 'outcome',)

    address = serializers.CharField(max_length=40)
    outcome = serializers.IntegerField()

    def create(self, validated_data):
        ultimate_oracle = None
        try:
            ultimate_oracle = models.UltimateOracle.objects.get(address=validated_data.get('address'))
            ultimate_oracle.total_amount = ultimate_oracle.challenge_amount
            ultimate_oracle.front_runner = validated_data.get('outcome')
            ultimate_oracle.front_runner_set_at_timestamp = mktime(datetime.now().timetuple())
            ultimate_oracle.save()
            return ultimate_oracle
        except models.UltimateOracle.DoesNotExist:
            raise serializers.ValidationError('UltimateOracle %s does not exist'.format(validated_data.get('address')))


class OutcomeVoteSerializer(ContractNotTimestampted, serializers.ModelSerializer):

    class Meta:
        model = models.UltimateOracle
        fields = ('address', 'sender', 'outcome', 'amount',)

    address = serializers.CharField(max_length=40)
    sender = serializers.CharField(max_length=40)
    outcome = serializers.IntegerField()
    amount = serializers.IntegerField()

    def create(self, validated_data):
        try:
            outcome_vote_balance = models.OutcomeVoteBalance.objects.get(address=validated_data.get('sender'),
                                                                         ultimate_oracle__address=validated_data.get('address'))
            outcome_vote_balance.balance += validated_data.get('amount')
            outcome_vote_balance.save()

            ultimate_oracle = models.UltimateOracle.objects.get(address=validated_data.get('address'))
            ultimate_oracle.total_amount += validated_data.get('amount')
            if validated_data.get('outcome') != ultimate_oracle.front_runner and \
                    ultimate_oracle.total_amount > ultimate_oracle.front_runner:
                ultimate_oracle.front_runner = validated_data.get('outcome')
                ultimate_oracle.front_runner_set_at_timestamp = mktime(datetime.now().timetuple())

            ultimate_oracle.save()
            return ultimate_oracle
        except models.OutcomeVoteBalance.DoesNotExist:
            raise serializers.ValidationError('OutcomeVoteBalance of UltimateOracle %s does not exist for '
                                              'sender address %s'
                                              .format(validated_data.get('address'), validated_data.get('sender')))
        except models.UltimateOracle.DoesNotExist:
            raise serializers.ValidationError('UltimateOracle %s does not exist'.format(validated_data.get('address')))


class WithdrawalSerializer(ContractNotTimestampted, serializers.ModelSerializer):

    class Meta:
        model = models.OutcomeVoteBalance
        fields = ('address', 'sender', 'amount',)

    address = serializers.CharField(max_length=40)
    sender = serializers.CharField(max_length=40)
    amount = serializers.IntegerField()

    def create(self, validated_data):
        try:
            outcome_vote_balance = models.OutcomeVoteBalance.objects.get(address=validated_data.get('sender'),
                                                                         ultimate_oracle__address=validated_data.get('address'))
            outcome_vote_balance.balance -= validated_data.get('amount')
            outcome_vote_balance.save()
            return outcome_vote_balance
        except models.OutcomeVoteBalance.DoesNotExist:
            raise serializers.ValidationError('OutcomeVoteBalance of UltimateOracle %s does not exist for '
                                              'sender address %s'
                                              .format(validated_data.get('address'), validated_data.get('sender')))


class OutcomeTokenPurchaseSerializer(ContractEventTimestamped, serializers.ModelSerializer):

    class Meta:
        model = models.BuyOrder
        fields = ContractEventTimestamped.Meta.fields + ('buyer', 'outcomeTokenIndex', 'outcomeTokenCount', 'cost',)

    address = serializers.CharField(max_length=40)
    buyer = serializers.CharField(max_length=40)
    outcomeTokenIndex = serializers.IntegerField()
    outcomeTokenCount = serializers.IntegerField()
    cost = serializers.IntegerField()

    def create(self, validated_data):
        try:
            market = models.Market.objects.get(address=validated_data.get('address'))
            token_index = validated_data.get('outcomeTokenIndex')
            token_count = validated_data.get('outcomeTokenCount')
            # Create Order
            order = models.BuyOrder()
            order.creation_date_time = validated_data['creation_date_time']
            order.creation_block = validated_data['creation_block']
            order.market = market
            order.sender = validated_data.get('buyer')
            order.outcome_token_index = token_index
            order.outcome_token_count = token_count
            order.cost = validated_data.get('cost')
            # Update token sale statistics
            logger.info('Market Net Sold: {}'.format(market.net_outcome_tokens_sold))
            # Update token sale statistics
            new_net_tokens_sold_stats = market.net_sold_tokens_copy_with_delta(index=token_index, delta=token_count)
            market.net_outcome_tokens_sold = new_net_tokens_sold_stats
            order.net_outcome_tokens_sold = new_net_tokens_sold_stats
            # Save order successfully, then save market changes
            order.save()
            market.save()
            return order
        except models.Market.DoesNotExist:
            raise serializers.ValidationError('Market with address %s does not exist.' % validated_data.get('address'))


class OutcomeTokenSaleSerializer(ContractEventTimestamped, serializers.ModelSerializer):

    class Meta:
        model = models.SellOrder
        fields = ContractEventTimestamped.Meta.fields + ('seller', 'outcomeTokenIndex', 'outcomeTokenCount', 'profit',)

    address = serializers.CharField(max_length=40)
    seller = serializers.CharField(max_length=40)
    outcomeTokenIndex = serializers.IntegerField()
    outcomeTokenCount = serializers.IntegerField()
    profit = serializers.IntegerField()

    def create(self, validated_data):
        try:
            market = models.Market.objects.get(address=validated_data.get('address'))
            token_index = validated_data.get('outcomeTokenIndex')
            token_count = validated_data.get('outcomeTokenCount')
            # Create Order
            order = models.SellOrder()
            order.creation_date_time = validated_data['creation_date_time']
            order.creation_block = validated_data['creation_block']
            order.market = market
            order.sender = validated_data.get('seller')
            order.outcome_token_index = token_index
            order.outcome_token_count = token_count
            order.profit = validated_data.get('profit')
            # TODO Update target token net amounts
            # Save order successfully, then save market changes
            order.save()
            # market.save()
            return order
        except models.Market.DoesNotExist:
            raise serializers.ValidationError('Market with address %s does not exist.' % validated_data.get('address'))


class OutcomeTokenShortSaleOrderSerializer(ContractEventTimestamped, serializers.ModelSerializer):

    class Meta:
        model = models.ShortSellOrder
        fields = ContractEventTimestamped.Meta.fields + ('buyer', 'outcomeTokenIndex', 'outcomeTokenCount', 'cost',)

    address = serializers.CharField(max_length=40)
    buyer = serializers.CharField(max_length=40)
    outcomeTokenIndex = serializers.IntegerField()
    outcomeTokenCount = serializers.IntegerField()
    cost = serializers.IntegerField()

    def create(self, validated_data):
        try:
            market = models.Market.objects.get(address=validated_data.get('address'))
            # Create Order
            order = models.ShortSellOrder()
            order.creation_date_time = validated_data['creation_date_time']
            order.creation_block = validated_data['creation_block']
            order.market = market
            order.sender = validated_data.get('buyer')
            order.outcome_token_index = validated_data.get('outcomeTokenIndex')
            order.outcome_token_count = validated_data.get('outcomeTokenCount')
            order.cost = validated_data.get('cost')
            # TODO Update target token net amounts
            # Update token sale statistics
            order.save()
            # market.save()
            return order
        except models.Market.DoesNotExist:
            raise serializers.ValidationError('Market with address %s does not exist.' % validated_data.get('address'))
