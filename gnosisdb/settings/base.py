from __future__ import absolute_import

from gnosisdb.adapters.mongo_adapter import MongoAdapter

GNOSISDB_DATABASE = {
    'ADAPTER': MongoAdapter,
    'URI': 'mongodb://mongo:27017/'
}

# TODO declare dictionary: collection => schema
GNOSISDB_SCHEMAS = {
    'CategoricalEvent': 'categorical_event.json',
    'ScalarEvent': 'scalar_event.json'
}

GNOSISDB_MAX_DOCUMENT_SIZE = 4096

GNOSISDB_VALIDATOR = None

API_PREFIX = 'gnosisdb'


