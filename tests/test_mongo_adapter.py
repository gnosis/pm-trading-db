from unittest import TestCase
from adapters.mongo_adapter import MongoAdapter


class TestMongoAdapter(TestCase):

    def setUp(self):
        self.config = {
            'uri': 'mongodb://mongo:27017/',
            'database': 'test'
        }
        self.adapter = MongoAdapter(self.config)
        self.assertIsNotNone(self.adapter)
        self.assertIsNotNone(self.adapter.config)

    def test_singleton(self):
        self.assertEqual(self.adapter, MongoAdapter(self.config))

    def test_connect(self):
        self.assertIsNone(self.adapter.database)
        self.adapter.connect()
        self.assertIsNotNone(self.adapter.database)
        result = self.adapter.database.test.count()
        self.assertEqual(result, 0)
