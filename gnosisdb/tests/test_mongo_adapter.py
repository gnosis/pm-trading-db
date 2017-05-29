from unittest import TestCase
from gnosisdb.adapters.mongo_adapter import MongoAdapter

class TestMongoAdapter(TestCase):

    def setUp(self):
        self.config = {
            'uri': 'mongodb://mongo:27017/',
            'database': 'adapter'
        }
        self.adapter = MongoAdapter(self.config)
        self.assertIsNotNone(self.adapter)
        self.assertIsNotNone(self.adapter.config)

    def tearDown(self):
        if self.adapter.client:
            self.adapter.client.drop_database(u"adapter")
            self.adapter.client = None
        self.adapter = None
        MongoAdapter._instances = {}

    def test_singleton(self):
        self.assertEqual(self.adapter, MongoAdapter(self.config))

    def test_connect(self):
        self.assertIsNone(self.adapter.client)
        self.adapter.connect()
        self.assertIsNotNone(self.adapter.client)
        result = self.adapter.client['adapter'].test.count()
        self.assertEqual(result, 0)

    def test_connect_fail(self):
        self.assertIsNone(self.adapter.client)
        self.config['uri'] = 'wrong://mongo:27017'
        self.assertIsNone(self.adapter.client)

    def test_write(self):
        self.adapter.connect()
        self.assertEqual(self.adapter.client['adapter'].test.count(), 0)
        self.adapter.write("test", None, {'test': 'insert'})
        self.assertEqual(self.adapter.client['adapter'].test.count(), 1)
        self.assertEqual(self.adapter.client['adapter'].test.find_one()[u'test'], u'insert')

    def test_disconnect(self):
        self.adapter.connect()
        self.adapter.disconnect()
        self.assertIsNone(self.adapter.client)