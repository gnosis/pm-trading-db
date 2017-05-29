from adapter import Adapter
from pymongo import MongoClient


class MongoAdapter(Adapter):

    def __init__(self, config):
        if config.get('uri') and config.get('database'):
            super(MongoAdapter, self).__init__(config)
        else:
            raise Exception("Adapter needs uri and database params")

    def connect(self):
        self.client = MongoClient(self.config['uri'])

    def disconnect(self):
        self.client.close()
        self.client = None

    def write(self, collection, schema, data):
        return self.client[self.config['database']][collection].insert_one(data)