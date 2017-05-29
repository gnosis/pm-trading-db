# PyCharm fix
from __future__ import absolute_import

import json
import unittest

from bitcoin import ecdsa_raw_sign
from ethereum.utils import sha3
from flask import Flask, request

from gnosisdb.adapters import adapter
from gnosisdb.flask_gnosisdb import GnosisDB


class TestFlaskExtension(unittest.TestCase):
    """python -m unittest tests.test_flask_extension"""

    def __init__(self, *args, **kwargs):
        super(TestFlaskExtension, self).__init__(*args, **kwargs)
        self.gnosisdb = None

    def setUp(self):
        self.app = Flask(__name__)
        self.test_client = self.app.test_client()
        self.gnosisdb = GnosisDB(self.app)

        self.v, self.r, self.s = ecdsa_raw_sign(sha3('test').encode('hex'), sha3(b'safe very safe').encode('hex'))

    def test_app_running(self):
        self.assertIsNotNone(self.gnosisdb)

    def test_routes(self):
        # not existing route check
        with self.app.test_request_context('/gnosisdb/doesNotExist'):
            self.assertEquals(404, request.routing_exception.code)

        # datas
        valid_data = {
            'collection': 'CategoricalEvent',
            'signature': {
                'r': self.r,
                's': self.s,
                'v': self.v
            },
            'data': {
                "title": "test",
                "description": "test",
                "resolutionDate": "2015-12-31T23:59:00Z",
                "outcomes": [0, 1]
            }
        }
        invalid_data = {
            'collection': 'CategoricalEvent',
            'signature': {
                'r': self.r,
                's': self.s,
                'v': self.v
            },
            'data': {
                "title": "test",
                "description": "test",
                "resolutionDate": "2015-12-31T23:59:00Z"
            }
        }
        invalid_data2 = {
            'collection': 'AWrongName',
            'signature': {
                'r': self.r,
                's': self.s,
                'v': self.v
            },
            'data': {
                "title": "test",
                "description": "test",
                "resolutionDate": "2015-12-31T23:59:00Z",
                "outcomes": [0, 1]
            }
        }

        valid_post_data = self.test_client.post(
            '/gnosisdb/',
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        invalid_post_data = self.test_client.post(
            '/gnosisdb/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        invalid_post_data2 = self.test_client.post(
            '/gnosisdb/',
            data=json.dumps(invalid_data2),
            content_type='application/json'
        )

        self.assertEquals(200, valid_post_data.status_code)
        self.assertEquals(400, invalid_post_data.status_code)
        self.assertEquals(400, invalid_post_data2.status_code)

        # test content length oversizes the maximum
        oversize_data = {
            'collection': 'CategoricalEvent',
            'signature': {
                'r': self.r,
                's': self.s,
                'v': self.v
            },
            'data': {
                'title': 'test',
                'description': 'test',
                'resolutionDate': '2015-12-31T23:59:00Z',
                'over': ''.join(['t' for x in range(8192)])
            }
        }
        oversize_post_data = self.test_client.post(
            '/gnosisdb/',
            data=json.dumps(oversize_data),
            content_type='application/json'
        )

        self.assertEquals(413, oversize_post_data.status_code)

    def test_config(self):
        self.assertIsNotNone(self.app.config.get('GNOSISDB_DATABASE'))

        TestClass = type('TestClass', (object,), {})

        TestOkClass = type('TestOkClass', (adapter.Adapter,), {})
        #TestOkClass.__new__()
        #self.assertIsInstance(TestOkClass({}), adapter.Adapter)


if __name__ == '__main__':
    unittest.main()
