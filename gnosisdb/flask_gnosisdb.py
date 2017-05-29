import json
import sys

from ethereum.utils import sha3
from flask import request
from flask_restful import Resource, Api, abort

from gnosisdb.adapters import adapter
from gnosisdb.auth import Auth
from gnosisdb.settings import base as base_config
from schema_validator import Validator, GnosisValidationError
from utils import limit_content_length

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


class GnosisAPI(Resource):
    """GnosisDB rest API class"""

    def __init__(self, *args, **kwargs):
        self.auth = Auth()
        self.validator = kwargs.get('validator')

    @limit_content_length(base_config.GNOSISDB_MAX_DOCUMENT_SIZE)
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
        # This is old eth_sign implementation
        # TODO use personal sign
        msg_hash = sha3(msg).encode('hex')

        # msg_hash = keccack256("\x19Ethereum Signed Message:\n" + len(message) + message))
        try:
            address = self.auth.recover_address(v, r, s, msg_hash)
        except Exception:
            abort(400, description='Not valid signature')

        # check if collection in available collections - retrieve info from config
        # schema = GnosisDB.get_schema_file_name(json_data.get('collection'))
        try:
            self.validator.set_schema(json_data.get('collection'))
        except Exception as e:
            abort(400, description=e.message)

        try:
            self.validator.validate(json_data.get('data'))
        except GnosisValidationError:
            abort(400, description='Invalid data')

        # TODO write data

        return {}


class GnosisDB(object):

    def __init__(self, app):
        self.API_PREFIX = '/gnosisdb/'
        self.validator = None
        self.app = app
        self.api = Api(self.app)
        self.init_app()

    def init_app(self):
        """Initializes the flask extension"""

        # load config
        self.__load_config()
        # load schemas and apply validator extension
        self.__load_validator()
        self.__load_schemas()
        # load api routes
        self.__load_api()

        # load adapter

        # Use the newstyle teardown_appcontext if it's available,
        # otherwise fall back to the request context
        if hasattr(self.app, 'teardown_appcontext'):
            self.app.teardown_appcontext(self.teardown)
        else:
            self.app.teardown_request(self.teardown)

    def teardown(self, exception):
        # do something on flask shutdown
        # TODO close adapter connection
        pass

    def __load_validator(self):
        """Loads the validator class and adds extensions"""
        self.validator = Validator()
        self.validator.extend_validator('date-time-ISO8601')

    def __load_schemas(self):
        """Loads the schemas declared in the Flask app configuration"""
        if not self.validator:
            self.__load_validator()

        schemas = self.app.config.get('GNOSISDB_SCHEMAS')
        self.validator.load_schemas(schemas)

    def __load_api(self):
        """Defines the API routes"""
        self.api.add_resource(GnosisAPI, self.API_PREFIX, resource_class_kwargs={'validator': self.validator})

    def __load_config(self):
        """Loads the base config and merges it with the Flask app configuration"""
        filez = self.__load_file('gnosisdb.settings.base')
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
        """Verifies if the user provided a compliant configuration
            Raises:
                Exception: if the a configuration field isn't valid
        """
        config_vars = [x for x in self.app.config.keys() if x.isupper() and 'GNOSISDB_' in x]

        if 'GNOSISDB_DATABASE' in config_vars:
            # _gnosisdb_database = config_vars[config_vars.index('GNOSISDB_DATABASE')]
            _gnosisdb_database = self.app.config.get('GNOSISDB_DATABASE')
            if not isinstance(_gnosisdb_database, dict):
                raise Exception('GNOSISDB_DATABASE must be a dictionary')

            if not 'ADAPTER' in _gnosisdb_database:
                raise Exception('GNOSISDB_DATABASE.ADAPTER is required')

            else:
                if not issubclass(_gnosisdb_database.get('ADAPTER'), adapter.Adapter):
                    raise Exception('Your adapter must inherit from Adapter')

            if not 'URI' in _gnosisdb_database:
                raise Exception('GNOSISDB_DATABASE.URI is required')

            # check the Adapter implements all the abstract methods
            methods = list(adapter.Adapter.__abstractmethods__)
            check = [method for method in _gnosisdb_database.get('ADAPTER').__dict__.keys() if x in list(adapter.Adapter.__abstractmethods__)]
            if not check or len(check) < len(methods):
                raise Exception('Please implement all the Adapter abstract methods: %s' % ', '.join([m for m in methods]))


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

    """
    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'mongo_db'):
                ctx.mongo_db = self.connect()
            return ctx.mongo_db
    """