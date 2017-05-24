# PyCharm fix
from __future__ import absolute_import
import os
import unittest
from pymongo import MongoClient


class TestMongo(unittest.TestCase):
    """python -m unittest tests.test_mongo"""

    def __init__(self, *args, **kwargs):
        super(TestMongo, self).__init__(*args, **kwargs)

    def setUp(self):
        self.client = MongoClient('mongo', 27017)
        self.db = self.client.test_db

    def test_connection(self):
        data = {'name': 'Giacomo'}
        _id = self.db.test_collection.insert_one(data).inserted_id
        self.assertIsNotNone(_id)
        db_data = self.db.test_collection.find_one({"_id": _id})
        self.assertEquals(data.get('name'), db_data.get('name'))



if __name__ == '__main__':
    unittest.main()
