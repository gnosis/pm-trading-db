# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from jsonschema.exceptions import ValidationError
from jsonschema import Draft4Validator, validators, validate
import datetime
import json
import pkg_resources

class GnosisValidationError(ValidationError):
    def __init__(self, *args, **kwargs):
        super(GnosisValidationError, self).__init__(*args, **kwargs)


class Validator(object):
    """JSON Schema Validator class"""

    def __init__(self, base_path='schemas'):
        self.base_path = pkg_resources.resource_filename('gnosisdb', base_path)
        self.schema = None
        self.schemas = None
        self.custom_validator = None

    def load_schema(self, file_name):
        # TODO delete
        """Loads a JSON Schema
        Args:
            file_name: the JSON file name, along with its .json exstension

        Raises:
            IOError: if the file doesn't exists
            ValueError: if the json file isn't well formatted
        """
        with open(self.base_path + '/' + file_name) as f:
            self.schema = json.load(f)

    def load_schemas(self, schemas):
        """Loads the JSON Schemas
        Args:
            schemas: a dictionary containing the collection name as key
                     and the file name as value

        Raises:
            IOError: if the file doesn't exists
            ValueError: if the json file isn't well formatted
        """
        self.schemas = {}
        for k, v in schemas.items():
            with open(self.base_path + '/' + v) as f:
                self.schemas.update({k:json.load(f)})

    def set_schema(self, schema_name):
        schema = self.schemas.get(schema_name)
        if not schema:
            raise Exception('Invalid collection')

        self.schema = schema

    def extend_validator(self, name):
        """Sets a custom validator extending a Draft4Validator
        Args:
            name: the validator name

        Raises:
            Exception: if the validator doesn't exists for the given name
        """
        custom_validator = self.get_custom_validator(name)

        if not custom_validator:
            raise Exception('%s validator is not available' % name)
        else:
            new_validators = {name: custom_validator}
            self.custom_validator = validators.extend(Draft4Validator, new_validators)

    def get_custom_validator(self, name):
        """Returns a suitable jsonschema custom validator function
        Args:
            name: the validator name

        Returns:
            The custom validator function, None otherwise.
        """
        if name == 'date-time-ISO8601':
            def date_time_validator(validator, format, instance, schema):
                if not validator.is_type(instance, "string"):
                    return
                try:
                    datetime.datetime.strptime(instance, format)
                except ValueError as ve:
                    yield ValidationError(ve.message)

            return date_time_validator

        return None

    def validate(self, data):
        """Validates a dictionary against a schema

        Args:
            data: A dictionary

        Returns:
            True for success, Exception otherwise.

        Raises:
            Exception: if schema is not provided
            GnosisValidationError: if data is cannot be validated
        """
        if not self.schema:
            raise Exception('Schema dictionary not provided')
        elif self.custom_validator:
            try:
                self.custom_validator(self.schema).validate(data)
                return True
            except ValidationError as ve:
                raise GnosisValidationError(ve.message)
        else:
            validate(data, self.schema)
            return True


