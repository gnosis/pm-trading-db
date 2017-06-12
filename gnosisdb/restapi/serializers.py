from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from relationaldb.models import EventDescription, ScalarEventDescription, CategoricalEventDescription, Oracle
from relationaldb.models import CentralizedOracle, UltimateOracle, Event, Market
from ipfsapi.exceptions import ErrorResponse
from gnosisdb.ipfs.ipfs import Ipfs


class ContractSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'address': instance.address,
            # 'factory_address': instance.factory_address,
            'creator': instance.creator,
            'creation_date': instance.creation_date,
            'creation_block': instance.creation_block
        }


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

        return result


class ScalarEventDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScalarEventDescription
        exclude = ('id',)


class CategoricalEventDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoricalEventDescription
        exclude = ('id',)


class IPFSEventDescriptionDeserializer(serializers.ModelSerializer):
    basic_fields = ('title', 'description', 'resolution_date',)
    scalar_fields = basic_fields + ('unit', 'decimals',)
    categorical_fields = basic_fields + ('outcomes',)

    class Meta:
        model = EventDescription
        fields = ('ipfs_hash',)

    def validate_ipfs_hash(self, value):
        ipfs = Ipfs()
        json_obj = None
        try:
            json_obj = ipfs.get(value)
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
        extracted['ipfs_hash'] = validated_data['ipfs_hash']
        instance = Serializer(data=extracted)
        instance.is_valid(raise_exception=True)
        result = instance.save()
        return result


class OracleSerializer(serializers.ModelSerializer):
    # TODO Dynamic way to display extra fields according to oracle type
    contract = ContractSerializer(source='*', many=False, read_only=True)
    is_outcome_set = serializers.BooleanField()
    outcome = serializers.IntegerField()

    class Meta:
        model = Oracle
        fields = ('contract', 'is_outcome_set', 'outcome')


class CentralizedOracleSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(source='*', many=False, read_only=True)
    is_outcome_set = serializers.BooleanField()
    outcome = serializers.IntegerField()
    owner = serializers.CharField(max_length=20)
    event_description = EventDescriptionSerializer(many=False, read_only=True)

    class Meta:
        model = CentralizedOracle
        fields = ('contract', 'is_outcome_set', 'outcome', 'owner', 'event_description')


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


class OutcomeTokenSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance.address


class EventSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(source='*', many=False, read_only=True)
    collateral_token = serializers.CharField()
    oracle = OracleSerializer(many=False, read_only=True)
    is_winning_outcome_set = serializers.BooleanField()
    winning_outcome = serializers.DecimalField(max_digits=80, decimal_places=0)
    # outcome_tokens = OutcomeTokenSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ('contract', 'collateral_token', 'oracle', 'is_winning_outcome_set', 'winning_outcome')


class IntegerCSVSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return map(int, instance.split(','))


class MarketSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(source='*', many=False, read_only=True)
    event = EventSerializer(many=False, read_only=True)
    market_maker = serializers.CharField()
    fee = serializers.IntegerField()
    funding = serializers.DecimalField(max_digits=80, decimal_places=0)
    net_outcome_tokens_sold = IntegerCSVSerializer(many=False, read_only=True)
    stage = serializers.IntegerField()

    class Meta:
        model = Market
        fields = ('contract', 'event', 'market_maker', 'fee', 'funding', 'net_outcome_tokens_sold', 'stage')
