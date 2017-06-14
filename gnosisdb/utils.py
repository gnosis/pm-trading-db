from functools import wraps
from rest_framework.response import Response
from rest_framework import status
import json


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