from rest_framework import serializers
from relationaldb import models
from restapi.serializers import IPFSEventDescriptionDeserializer

# Declare basic fields, join params on root object and
class ContractSerializer(serializers.BaseSerializer):
    class Meta:
        fields = ('factory', 'creator', 'creation_date', 'creation_block', )

    # address = serializers.CharField()
    factory = serializers.CharField(max_length=22)  # included prefix
    creation_date = serializers.DateTimeField()
    creation_block = serializers.IntegerField()
    creator = serializers.CharField(max_length=22)

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


class CentralizedOracleSerializer(ContractSerializer, serializers.ModelSerializer):
    
    class Meta:
        model = models.CentralizedOracle
        fields = ContractSerializer.Meta.fields + ('ipfsHash', 'centralizedOracle')

    # owner = serializers.CharField(max_length=22)
    centralizedOracle = serializers.CharField(max_length=22, source='address')
    ipfsHash = IPFSEventDescriptionDeserializer(source='event_description')

    # def to_internal_value(self, data):
    #     data['owner'] = data['creator']
    #     data['address'] = data.pop('centralizedOracle')
    #     data['is_outcome_set'] = False
    #     data['event_description'] = data.pop('ipfsHash')
    #     return data

    # ipfs_hash

    # def to_internal_value(self, data):
    #     i = super(CentralizedOracleSerializer, self).to_internal_value(data)
    #     return i