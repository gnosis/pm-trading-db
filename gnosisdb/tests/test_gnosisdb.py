# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.test import TestCase
from django.core.urlresolvers import reverse
from bitcoin import ecdsa_raw_sign
from ethereum.utils import sha3
from json import dumps
from GnosisDB import GnosisDB

class TestGnosisDB(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestGnosisDB, self).__init__(*args, **kwargs)
        self.gnosisdb = None

    def setUp(self):
        self.gnosisdb = GnosisDB()
        self.v, self.r, self.s = ecdsa_raw_sign(sha3('test').encode('hex'), sha3(b'safe very safe').encode('hex'))

    def test_app_running(self):
        self.assertIsNotNone(self.gnosisdb)

    def test_routes(self):
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

        valid_post_data = self.client.post(
            reverse('create'),
            data=dumps(valid_data),
            content_type='application/json'
        )
        invalid_post_data = self.client.post(
            reverse('create'),
            data=dumps(invalid_data),
            content_type='application/json'
        )
        invalid_post_data2 = self.client.post(
            reverse('create'),
            data=dumps(invalid_data2),
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
        oversize_post_data = self.client.post(
            reverse('create'),
            data=dumps(oversize_data),
            content_type='application/json'
        )

        self.assertEquals(413, oversize_post_data.status_code)
    """
    def test_config(self):
        self.assertIsNotNone(self.app.config.get('GNOSISDB_DATABASE'))
        TestKoClass = type('TestKoClass', (object,), {})
        TestOkClass = type('TestOkClass', (adapter.Adapter,), {'connect': lambda x: x, 'disconnect': lambda x: x, 'write': lambda x: x})
        TestOkClassNoImpl = type('TestKoClass', (adapter.Adapter,), {}) # this doesn't implement the abstract methods
        self.assertIsInstance(TestOkClass({}), adapter.Adapter)
        self.assertNotIsInstance(TestKoClass(), adapter.Adapter)

        app2 = Flask(__name__)
        # not valid configuration
        app2.config['GNOSISDB_DATABASE'] = {
            'ADAPTER': TestKoClass,
            'URI': 'mongodb://mongo:27017/'
        }

        with self.assertRaises(Exception):
            GnosisDB(app2)

        # not valid configuration
        app2.config['GNOSISDB_DATABASE'] = {
            'ADAPTER': TestOkClassNoImpl,
            'URI': 'mongodb://mongo:27017/'
        }

        with self.assertRaises(Exception):
            GnosisDB(app2)

        # not valid configuration
        app2.config['GNOSISDB_DATABASE'] = {
            'URI': 'mongodb://mongo:27017/'
        }

        with self.assertRaises(Exception):
            GnosisDB(app2)

        # not valid configuration
        app2.config['GNOSISDB_DATABASE'] = {
            'ADAPTER': TestKoClass,
        }

        with self.assertRaises(Exception):
            GnosisDB(app2)
    """
