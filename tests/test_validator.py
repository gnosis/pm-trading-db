# PyCharm fix
from __future__ import absolute_import
import unittest
import json
from jsonschema import Draft4Validator, validators
from jsonschema.exceptions import ValidationError
from schema_validator import Validator
import datetime


class TestValidator(unittest.TestCase):
    """python -m unittest tests.test_validator"""

    def __init__(self, *args, **kwargs):
        super(TestValidator, self).__init__(*args, **kwargs)

    def test_validator_extension(self):
        schema = None

        with open('schemas/categorical_event.json') as f:
            schema = json.load(f)

        valid_data = {
            "title": "test",
            "description": "test",
            "resolutionDate": "2015-12-31T23:59:00Z",
            "outcomes": [0, 1]
        }

        invalid_data = {
            "title": "test",
            "description": "test",
            "resolutionDate": "2015-12-31",
            "outcomes": [0, 1]
        }

        # Creating a custom date-time validator
        def date_validator(validator, format, instance, schema):
            if not validator.is_type(instance, "string"):
                return

            try:
                datetime.datetime.strptime(instance, format)
            except ValueError as ve:
                yield ValidationError(ve.message)

        new_validators = {
            'date-time': date_validator
        }

        GnosisValidator = validators.extend(Draft4Validator, validators=new_validators)
        GnosisValidator(schema).validate(valid_data)

        with self.assertRaises(ValidationError):
            GnosisValidator(schema).validate(invalid_data)

    def test_validator_errors(self):
        valid_scalar_data = {
            "title": "test",
            "description": "test",
            "resolutionDate": "2015-12-31T23:59:00Z",
            "unit": "MilliBit",
            "decimals": 10
        }

        validator = Validator()

        with self.assertRaises(Exception):
            validator.validate(valid_scalar_data)

        validator.load_schema('scalar_event.json')

        with self.assertRaises(Exception):
            validator.validate()

        validator.validate(valid_scalar_data)

        # test custom validator
        with self.assertRaises(Exception):
            validator.extend_validator('test')

        validator.extend_validator('date-time')
        self.assertIsNotNone(validator.custom_validator)

    def test_validator(self):

        valid_categorical_data = {
            "title": "test",
            "description": "test",
            "resolutionDate": "2015-12-31T23:59:00Z",
            "outcomes": [0, 1]
        }

        invalid_categorical_data = {
            "title": "test",
            "description": "test",
            "resolutionDate": "2015-12-31",
            "outcomes": [0, 1]
        }

        valid_scalar_data = {
            "title": "test",
            "description": "test",
            "resolutionDate": "2015-12-31T23:59:00Z",
            "unit": "MilliBit",
            "decimals": 10
        }

        # Empty title
        invalid_scalar_data = {
            "title": "",
            "description": "test",
            "resolutionDate": "2015-12-31",
            "unit": "MilliBit",
            "decimals": 10
        }

        validator = Validator()
        # test categorical_event first
        validator.load_schema('categorical_event.json')
        validator.extend_validator('date-time')
        validator.validate(valid_categorical_data)

        with self.assertRaises(ValidationError):
            validator.validate(invalid_categorical_data)

        # Set a valid resolutionDate
        invalid_categorical_data['resolutionDate'] = valid_categorical_data['resolutionDate']
        # Remove 1 item from outcomes
        invalid_categorical_data['outcomes'].pop()

        with self.assertRaises(ValidationError):
            validator.validate(invalid_categorical_data)

        # Reach the outcomes min-length
        invalid_categorical_data['outcomes'].append(1)
        validator.validate(valid_categorical_data)

        # load an invalid file
        with self.assertRaises(IOError):
            validator.load_schema('fake.json')

        # test scalar event
        validator.load_schema('scalar_event.json')
        validator.validate(valid_scalar_data)

        with self.assertRaises(ValidationError):
            validator.validate(invalid_scalar_data)


if __name__ == '__main__':
    unittest.main()
