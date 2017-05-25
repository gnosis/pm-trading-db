from adapter import Adapter
from pymongo import MongoClient


class MongoAdapter(Adapter):

    def __init__(self, config):
        if config.get('uri') and config.get('database'):
            super(MongoAdapter, self).__init__(config)
        else:
            raise Exception("Adapter needs uri and database params")

    def connect(self):
        self.database = MongoClient(self.config['uri'])[self.config['database']]

    def disconnect(self):
        pass

    def write(self, collection, schema, data):
        pass