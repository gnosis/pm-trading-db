from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from gnosisdb.relationaldb.models import ScalarEventDescription, CategoricalEventDescription, Oracle
from gnosisdb.relationaldb.models import CentralizedOracle, UltimateOracle


class ContractSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'address': instance.address,
            'factory_address': instance.factory_address,
            'creator': instance.creator,
            'creation_date': instance.creation_date,
            'creation_block': instance.creation_block
        }


class EventDescriptionSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        result = {
            'title': instance.title,
            'description': instance.description,
            'resolution_date': instance.resolution_date
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


class OracleSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(source='*', many=False, read_only=True)
    is_outcome_set = serializers.BooleanField()
    outcome = serializers.DecimalField(max_digits=80, decimal_places=0)

    class Meta:
        model = Oracle
        fields = ('contract', 'is_outcome_set', 'outcome')


class CentralizedOracleSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(source='*', many=False, read_only=True)
    is_outcome_set = serializers.BooleanField()
    outcome = serializers.DecimalField(max_digits=80, decimal_places=0)
    owner = serializers.CharField(max_length=20)
    ipfs_hash = serializers.CharField()
    event_description = EventDescriptionSerializer(many=False, read_only=True)

    class Meta:
        model = CentralizedOracle
        fields = ('creator', 'contract', 'is_outcome_set', 'outcome', 'owner', 'ipfs_hash', 'event_description')


class UltimateOracleSerializer(serializers.ModelSerializer):
    contract = ContractSerializer(source='*', many=False, read_only=True)
    is_outcome_set = serializers.BooleanField()
    outcome = serializers.DecimalField(max_digits=80, decimal_places=0)
    forwarded_oracle = OracleSerializer(many=False, read_only=True)
    collateral_token = serializers.CharField(source='collateral_token.address')
    spread_multiplier = serializers.DecimalField(max_digits=80, decimal_places=0)
    challenge_period = serializers.DecimalField(max_digits=80, decimal_places=0)
    challenge_amount = serializers.DecimalField(max_digits=80, decimal_places=0)
    front_runner_period = serializers.DecimalField(max_digits=80, decimal_places=0)
    forwarded_outcome = serializers.DecimalField(max_digits=80, decimal_places=0)
    outcome_set_at_timestamp = serializers.DecimalField(max_digits=80, decimal_places=0)
    front_runner = serializers.DecimalField(max_digits=80, decimal_places=0)
    front_runner_set_at_timestamp = serializers.DecimalField(max_digits=80, decimal_places=0)
    total_amount = serializers.DecimalField(max_digits=80, decimal_places=0)

    class Meta:
        model = UltimateOracle
        fields = ('contract', 'is_outcome_set', 'outcome', 'collateral_token', 'spread_multiplier', 'challenge_period',
                  'challenge_amount', 'front_runner_period', 'forwarded_outcome', 'outcome_set_at_timestamp',
                  'front_runner', 'front_runner_set_at_timestamp', 'total_amount', 'forwarded_oracle')
