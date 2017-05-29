from flask_restful import Resource, Api, abort
from flask import request
from schema_validator import Validator, GnosisValidationError
from auth import Auth
from utils import limit_content_length
from ethereum.utils import sha3
from adapters import adapter
import json
import sys

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

    # TODO get from config
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
        # TODO Do data field object
        msg = json.dumps(json_data.get('data'), separators=(',', ':'))
        # This is old eth_sign implementation
        # TODO use personal sign
        msg_hash = sha3(msg).encode('hex')
        try:
            address = self.auth.recover_address(v, r, s, msg_hash)
        except Exception:
            abort(400, description='Not valid signature')

        # check if collection in available collections - retrieve info from config
        # TODO get schema from memory (dict)
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
        # load config
        self.__load_config()
        # load api routes
        self.__load_api()

        # TODO load schemas and apply validator extension

        # load adapter

        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(self.app, 'teardown_appcontext'):
            self.app.teardown_appcontext(self.teardown)
        else:
            self.app.teardown_request(self.teardown)

    def teardown(self, exception):
        # do something on flask shutdown
        pass

    def __load_api(self):
        """Defines the API routes"""
        self.api.add_resource(GnosisAPI, self.API_PREFIX)

    def __load_config(self):
        filez = self.__load_file('settings.base')
        variables = [x for x in dir(filez) if x.isupper() and 'GNOSISDB' in x]
        default_config = {}
        # set default config values
        for var in variables:
            default_config.update({
                var: filez.__dict__[var]
            })

        # if not config valid then raise error
        self.__check_user_config()
        # get Flask config and filter by GNOSISDB_
        flask_config = {k:v for k,v in self.app.config.iteritems() if 'GNOSISDB_' in k}
        # merge Flask GNOSIS config into default_config
        default_config.update(flask_config)
        # load configuration
        self.app.config.update(default_config)

    def __check_user_config(self):
        # todo, verify if the user provided a compliant configuration
        config_vars = [x for x in self.app.config.keys() if x.isupper() and 'GNOSISDB_' in x]

        if 'GNOSISDB_DATABASE' in config_vars:
            _gnosisdb_database = config_vars[config_vars.index('GNOSISDB_DATABASE')]
            if not isinstance(_gnosisdb_database, dict):
                raise Exception('GNOSISDB_DATABASE must be a dictionary')

            if not 'ADAPTER' in _gnosisdb_database:
                raise Exception('GNOSISDB_DATABASE.ADAPTER is required')

            else:
                if not isinstance(_gnosisdb_database.get('ADAPTER'), adapter.Adapter):
                    raise Exception('Your adapter must inherit from Adapter')

            if not 'URI' in _gnosisdb_database:
                raise Exception('GNOSISDB_DATABASE.URI is required')

    def __load_file(self, import_name, silent=False):
        """Imports an object based on a string.  This is useful if you want to
        use import paths as endpoints or something similar.  An import path can
        be specified either in dotted notation (``xml.sax.saxutils.escape``)
        or with a colon as object delimiter (``xml.sax.saxutils:escape``).

        If `silent` is True the return value will be `None` if the import fails.

        :param import_name: the dotted name for the object to import.
        :param silent: if set to `True` import errors are ignored and
                       `None` is returned instead.
        :return: imported object
        """
        # force the import name to automatically convert to strings
        # __import__ is not able to handle unicode strings in the fromlist
        # if the module is a package
        import_name = str(import_name).replace(':', '.')
        try:
            try:
                __import__(import_name)
            except ImportError:
                if '.' not in import_name:
                    raise
            else:
                return sys.modules[import_name]

            module_name, obj_name = import_name.rsplit('.', 1)
            try:
                module = __import__(module_name, None, None, [obj_name])
            except ImportError:
                # support importing modules not yet set up by the parent module
                # (or package for that matter)
                module = self.__load_file(module_name)

            try:
                return getattr(module, obj_name)
            except AttributeError as e:
                raise ImportError(e)

        except ImportError as e:
            if not silent:
                raise Exception(sys.exc_info()[2])

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