# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from validators.schema_validator import Validator
from adapters import adapter
from django.conf import settings
import sys


class GnosisDB(object):

    def __init__(self):
        self.validator = None
        self.init_app()

    def init_app(self):
        """Initializes the flask extension"""

        # load config
        self.__load_config()
        # load schemas and apply validator extension
        self.__load_validator()
        self.__load_schemas()

        # load adapter

    def __load_validator(self):
        """Loads the validator class and adds extensions"""
        self.validator = Validator()
        self.validator.extend_validator('date-time-ISO8601')
        setattr(settings, 'GNOSISDB_VALIDATOR', self.validator)

    def __load_schemas(self):
        """Loads the schemas declared in the Flask app configuration"""
        if not self.validator:
            self.__load_validator()

        schemas = getattr(settings, 'GNOSISDB_SCHEMAS')
        self.validator.load_schemas(schemas)

    def __load_config(self):
        """Loads the base config and merges it with the Django app configuration"""
        filez = self.__load_file('gnosisdb.settings.base')
        variables = [x for x in dir(filez) if x.isupper() and 'GNOSISDB' in x]
        default_config = {}
        # set default config values
        for var in variables:
            if not hasattr(settings, var):
                setattr(settings, var, filez.__dict__[var])
            #default_config.update({
            #    var: filez.__dict__[var]
            #})

        # if not config valid then raise error
        self.__check_user_config()

        # get Flask config and filter by GNOSISDB_
        # django_config = {k:v for k,v in dir(settings) if 'GNOSISDB_' in k}

        # merge Flask GNOSIS config into default_config
        # default_config.update(django_config)
        # load configuration
        # self.app.config.update(default_config)

    def __check_user_config(self):
        """Verifies if the user provided a compliant configuration
            Raises:
                Exception: if the a configuration field isn't valid
        """
        config_vars = [x for x in dir(settings) if x.isupper() and 'GNOSISDB_' in x]

        if 'GNOSISDB_DATABASE' in config_vars:
            # _gnosisdb_database = config_vars[config_vars.index('GNOSISDB_DATABASE')]
            _gnosisdb_database = getattr(settings, 'GNOSISDB_DATABASE')
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
            check = [method for method in _gnosisdb_database.get('ADAPTER').__dict__.keys() if method in list(adapter.Adapter.__abstractmethods__)]
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
                raise Exception(sys.exc_info()[1])