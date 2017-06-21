from django.core.exceptions import ValidationError
from json import loads

def validate_numeric_dictionary(value):
    if value is None or len(value) == 0:
        return

    try:
        obj = loads(value)
    except Exception:
        raise ValidationError("Field is not a valid JSON object.")

    if not isinstance(obj, dict):
        raise ValidationError("Field is not a dictionary.")

    for key in obj:
        if not key.isdigit():
            raise ValidationError("Field contains non-numeric indices.")
        elif not isinstance(obj[key], int):
            raise ValidationError("Field contains non-numeric values.")
