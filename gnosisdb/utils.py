from functools import wraps
from flask import request, abort


def limit_content_length(max_length):
    """Rejects requests whose content oversize the maximum allowed

    Args:
        max_length: maximum content-length allowed
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            cl = request.content_length
            if cl is not None and cl > max_length:
                abort(413)
            return f(*args, **kwargs)
        return wrapper
    return decorator

def singleton(clazz):
    instances = {}
    def getinstance(*args, **kwargs):
        if clazz not in instances:
            instances[clazz] = clazz(*args, **kwargs)
        return instances[clazz]
    return getinstance
