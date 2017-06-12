from rest_framework import serializers
from relationaldb import models


# Declare basic fields, join params on root object and
class ContractSerializer(serializers.BaseSerializer):
    class Meta:
        fields = ('factory', 'address', 'creator', 'creation_date', 'creation_block', )

    factory = serializers.CharField(max_length=22)  # included prefix
    creation_date = serializers.DateTimeField()
    creation_block = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        self.block = kwargs.pop('block')

        data = kwargs.pop('data')
        # Event params moved to root object
        new_data = {
            'address': data[u'address'],
            'creation_date': self.block.get('timestamp'),
            'creation_block': self.block.get('number')
        }

        for param in data.get('params'):
            new_data[param[u'name']] = param[u'value']

        kwargs['data'] = new_data
        super(ContractSerializer, self).__init__(*args, **kwargs)

    # def to_internal_value(self, data):
    #     factory = data.get('address')
    #     if not factory:
    #         raise serializers.ValidationError('Invalid event, factory address needed')
    #
    #     internal_value = {
    #         'factory': factory,
    #         'creation_date': self.block.get('timestamp'),
    #         'creation_block': self.block.get('number')
    #     }
    #
    #     return internal_value


class CentralizedOracleSerializer(ContractSerializer, serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        s = super(CentralizedOracleSerializer, self).__init__(*args, **kwargs)
        pass
    
    class Meta:
        model = models.CentralizedOracle
        fields = ContractSerializer.Meta.fields + ('owner', )

    address = serializers.CharField(max_length=22, source='centralizedOracle')
    creator = serializers.CharField(max_length=22)
    owner = serializers.CharField(max_length=22, source='creator')

    def validate(self, attrs):
        pass

    # ipfs_hash

    # def to_internal_value(self, data):
    #     i = super(CentralizedOracleSerializer, self).to_internal_value(data)
    #     return i