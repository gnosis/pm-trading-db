from adapters.mongo_adapter import MongoAdapter

GNOSISDB_DATABASE = {
    'ADAPTER': MongoAdapter,
    'URI': 'mongodb://mongo:27017/'
}

# TODO declare dictionary: collection => schema

GNOSISDB_MAX_DOCUMENT_SIZE = 4096




