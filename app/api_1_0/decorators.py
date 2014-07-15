from functools import wraps
from flask import g
from .errors import forbidden
from app.models import AnonymousBrewer


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.get('current_user', AnonymousBrewer()).can(permission):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
