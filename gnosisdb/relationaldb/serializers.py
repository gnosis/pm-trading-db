from rest_framework import serializers
from relationaldb import models


# Declare basic fields, join params on root object and
class ContractSerializer(serializers.BaseSerializer):
    def to_internal_value(self, data):
        factory = data.get('address')

        internal_value = {
            'factory': factory
        }

        for param in data.get('params'):
            internal_value[param[u'name']] = param[u'value']


class CentralizedOracleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CentralizedOracle
        extra_kwargs = {'block': {'write_only': True}}

    factory = serializers.CharField(max_length=22) # included prefix
    address = serializers.CharField(max_length=22, source='centralizedOracleCreation')
    creator = serializers.CharField(max_length=22, source='creator')