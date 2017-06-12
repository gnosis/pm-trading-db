from rest_framework import serializers
from rest_framework.fields import CharField
from relationaldb import models
from ipfs.ipfs import Ipfs


# Declare basic fields, join params on root object and
class ContractSerializer(serializers.BaseSerializer):
    class Meta:
        fields = ('factory', 'creator', 'creation_date', 'creation_block', )

    # address = serializers.CharField()
    factory = serializers.CharField(max_length=20)  # included prefix
    creation_date = serializers.DateTimeField()
    creation_block = serializers.IntegerField()
    creator = serializers.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        self.block = kwargs.pop('block')
        super(ContractSerializer, self).__init__(*args, **kwargs)
        data = kwargs.pop('data')
        # Event params moved to root object
        new_data = {
            'factory': data[u'address'],
            'creation_date': self.block.get('timestamp'),
            'creation_block': self.block.get('number')
        }

        for param in data.get('params'):
            new_data[param[u'name']] = param[u'value']

        self.initial_data = new_data


class IpfsHashField(CharField):

    def __init__(self, **kwargs):
        super(IpfsHashField, self).__init__(**kwargs)

    def get_event_description(self, ipfs_hash):
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
                return event_description # None

            # add ipfs_hash to description_json
            event_description_json.update({'ipfs_hash': data})

            if 'outcomes' in event_description_json:
                # categorical
                event_description = models.CategoricalEventDescription.objects.create(event_description_json)

            elif 'decimals' in event_description:
                #scalar
                event_description = models.ScalarEventDescription.objects.create(event_description_json)

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


class CentralizedOracleSerializer(ContractSerializer, serializers.ModelSerializer):
    
    class Meta:
        model = models.CentralizedOracle
        fields = ContractSerializer.Meta.fields + ('ipfsHash', 'centralizedOracle')

    centralizedOracle = serializers.CharField(max_length=20, source='address')
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
    creator = serializers.CharField(max_length=20)
    oracle = OracleField
    # outcomeCount = serializers.IntegerField(source='outcome_count')


class ScalarEventSerializer(EventSerializer, serializers.ModelSerializer):

    class Meta:
        model = models.ScalarEvent
        fields = EventSerializer.Meta.fields + ('lowerBound', 'upperBound',)

    lowerBound = serializers.IntegerField(source='lower_bound')
    upperBound = serializers.IntegerField(source='upper_bound')
