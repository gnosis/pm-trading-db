from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema import Draft4Validator, validators, validate
import datetime
import json


class GnosisValidationError(ValidationError):
    def __init__(self, *args, **kwargs):
        super(GnosisValidationError, self).__init__(*args, **kwargs)


class Validator(object):
    """JSON Schema Validator class"""

    def __init__(self, base_path='schemas'):
        self.base_path = base_path
        self.schema = None
        self.custom_validator = None

    def load_schema(self, file_name):
        """Loads a JSON Schema
        Args:
            file_name: the JSON file name, along with its .json exstension

        Raises:
            IOError: if the file doesn't exists
            ValueError: if the json file isn't well formatted
        """
        with open(self.base_path + '/' + file_name) as f:
            self.schema = json.load(f)

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
                raise GnosisValidationError(ve)
        else:
            validate(data, self.schema)
            return True


