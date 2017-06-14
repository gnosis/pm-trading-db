from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.utils.module_loading import import_string
from settings_utils.address_getter import AbstractAddressesGetter
import json
import inspect


def limit_content_length(max_length):
    """Rejects requests whose content oversize the maximum allowed

    Args:
        max_length: maximum content-length allowed
    """
    def decorator(f):
        @wraps(f)
        def wrapper(instance, request,*args, **kwargs):
            content_length = len(json.dumps(request.data))
            if content_length is not None and content_length > max_length:
                return Response(status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, data={})
            return f(instance, request, *args, **kwargs)
        return wrapper
    return decorator


def singleton(clazz):
    instances = {}
    def getinstance(*args, **kwargs):
        if clazz not in instances:
            instances[clazz] = clazz(*args, **kwargs)
        return instances[clazz]
    return getinstance


def addresses_getter(module_path):
    """Returns the addresses list.

    :param module_path: a dot separated module path
    :return: array of strings
    """
    if isinstance(module_path, str):
        # check str is a module path, load it and retrieve addresses array
        reference = import_string(module_path)
        if inspect.isclass(reference):
            if issubclass(reference, AbstractAddressesGetter):
                return reference().get_addresses()
            else:
                raise ImportError("AddressesGetter class must inherit from %s " % str(AbstractAddressesGetter.__name__))
        elif inspect.isfunction(reference):
            return reference()
        else:
            raise ImportError("%s doesn't look like a module path" % module_path)
    else:
        raise ImportError("%s doesn't look like a module path" % module_path)
