from flask_restful import Resource, Api, abort
from flask import request
from schema_validator import Validator, GnosisValidationError
from auth import Auth
from utils import limit_content_length
from ethereum.utils import sha3
import json

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class GnosisAPI(Resource):

    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        self.validator = Validator()
        self.auth = Auth()

    @limit_content_length(8192)
    def post(self):
        schema = None
        address = None
        json_data = request.get_json()

        # check all required main fields
        if 'collection' not in json_data or 'signature' not in json_data \
                or 'data' not in json_data:
            abort(400, description='Bad request')

        # check signature
        if 'v' not in json_data.get('signature') or 'r' not in json_data.get('signature') \
                or 's' not in json_data.get('signature'):
            abort(400, description='Bad request')

        v = json_data.get('signature').get('v')
        r = json_data.get('signature').get('r')
        s = json_data.get('signature').get('s')
        msg = json.dumps(json_data.get('data'), separators=(',', ':'))
        msg_hash = sha3(msg).encode('hex')
        try:
            address = self.auth.recover_address(v, r, s, msg_hash)
        except Exception:
            abort(400, description='Not valid signature')

        # check if collection in available collections - retrieve info from config
        schema = GnosisDB.get_schema_file_name(json_data.get('collection'))

        if not schema:
            abort(400, description='Invalid collection')

        # validate schema
        self.validator.load_schema(schema)
        self.validator.extend_validator('date-time-ISO8601')
        try:
            self.validator.validate(json_data.get('data'))
        except GnosisValidationError:
            abort(400, description='Invalid data')

        # TODO write data

        return {}


class GnosisDB(object):

    def __init__(self, app):
        self.API_PREFIX = '/gnosisdb/'
        self.app = app
        self.api = Api(self.app)
        self.init_app()

    def init_app(self):
        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(self.app, 'teardown_appcontext'):
            self.app.teardown_appcontext(self.teardown)
        else:
            self.app.teardown_request(self.teardown)

        # load api routes
        self.__load_api()

        # load adapter


    def teardown(self, exception):
        # do something on flask shutdown
        pass

    def __load_api(self):
        """Defines the API routes"""
        self.api.add_resource(GnosisAPI, self.API_PREFIX)

    @staticmethod
    def get_schema_file_name(collection_name):
        if collection_name == 'CategoricalEvent':
            return 'categorical_event.json'
        elif collection_name == 'ScalarEvent':
            return 'scalar_Event.json'
        else:
            return None



    """
    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'mongo_db'):
                ctx.mongo_db = self.connect()
            return ctx.mongo_db
    """