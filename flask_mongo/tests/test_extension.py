from __future__ import absolute_import
from flask_mongo.flask_mongo import Mongo
from flask import Flask
import unittest


class TestExtension(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestExtension, self).__init__(*args, **kwargs)

    def setUp(self):
        self.app = Flask(__name__)
        self.db = Mongo(self.app)

    def test_connection(self):
        with self.app.app_context():
            connection = self.db.connection
            self.assertIsNotNone(connection)
            _id = connection.test_db.test_collection.insert_one({'name': 'Giacomo'}).inserted_id
            self.assertIsNotNone(_id)


