from rest_framework import serializers
from rest_framework.fields import CharField
from relationaldb import models
from ipfs.ipfs import Ipfs
from datetime import datetime
from ipfsapi.exceptions import ErrorResponse


# Declare basic fields, join params on root object and
class ContractSerializer(serializers.BaseSerializer):
    class Meta:
        fields = ('factory', 'creator', 'creation_date', 'creation_block', )

    # address = serializers.CharField()
    factory = serializers.CharField(max_length=40)  # included prefix
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    creation_block = serializers.IntegerField()
    creator = serializers.CharField(max_length=40)

    def __init__(self, *args, **kwargs):
        self.block = kwargs.pop('block')
        super(ContractSerializer, self).__init__(*args, **kwargs)
        data = kwargs.pop('data')
        # Event params moved to root object
        new_data = {
            'factory': data[u'address'],
            'creation_date': datetime.fromtimestamp(self.block.get('timestamp')),
            'creation_block': self.block.get('number')
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
        if address_len > 20:
            raise serializers.ValidationError('Maximum address length of 20 chars')
        elif address_len < 20:
            raise serializers.ValidationError('Address must have 20 chars')
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


class CentralizedOracleSerializer(ContractSerializer, serializers.ModelSerializer):
    
    class Meta:
        model = models.CentralizedOracle
        fields = ContractSerializer.Meta.fields + ('ipfsHash', 'centralizedOracle')

    centralizedOracle = serializers.CharField(max_length=40, source='address')
    ipfsHash = IpfsHashField(source='event_description')


class UltimateOracleSerializer(ContractSerializer, serializers.ModelSerializer):

    class Meta:
        model = models.UltimateOracle
        fields = ContractSerializer.Meta.fields + ('ultimateOracle', 'oracle', 'collateralToken',
                                                   'spreadMultiplier', 'challengePeriod', 'challengeAmount',
                                                   'frontRunnerPeriod')
    ultimateOracle = serializers.CharField(max_length=20, source='address')
    oracle = OracleField(source='forwarded_oracle')
    collateralToken = serializers.CharField(max_length=20, source='collateral_token')
    spreadMultiplier = serializers.IntegerField(source='spread_multiplier')
    challengePeriod = serializers.IntegerField(source='challenge_period')
    challengeAmount = serializers.IntegerField(source='challenge_amount')
    frontRunnerPeriod = serializers.IntegerField(source='front_runner_period')


class EventSerializer(ContractSerializer, serializers.ModelSerializer):

    class Meta:
        models = models.Event
        fields = ContractSerializer.Meta.fields + ('collateralToken', 'creator', 'oracle',)

    collateralToken = serializers.CharField(max_length=20, source='collateral_token')
    creator = serializers.CharField(max_length=40)
    oracle = OracleField()


class ScalarEventSerializer(EventSerializer, serializers.ModelSerializer):

    class Meta:
        model = models.ScalarEvent
        fields = EventSerializer.Meta.fields + ('lowerBound', 'upperBound', 'scalarEvent')

    lowerBound = serializers.IntegerField(source='lower_bound')
    upperBound = serializers.IntegerField(source='upper_bound')
    scalarEvent = serializers.CharField(source='address', max_length=20)


class CategoricalEventSerializer(EventSerializer, serializers.ModelSerializer):
    class Meta:
        model = models.CategoricalEvent
        fields = EventSerializer.Meta.fields + ('categoricalEvent',)

    categoricalEvent = serializers.CharField(source='address', max_length=20)


class MarketSerializer(ContractSerializer, serializers.ModelSerializer):

    class Meta:
        model = models.Market
        fields = ContractSerializer.Meta.fields + ('eventContract', 'marketMaker', 'fee',)

    eventContract = EventField(source='event')
    marketMaker = serializers.CharField(max_length=20, source='market_maker')
    fee = serializers.IntegerField()


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
