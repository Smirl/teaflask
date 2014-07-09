"""Useful decorators for the app."""

from functools import wraps
from flask import abort, request
from flask.ext.login import current_user
from .models import Permission, Brewer
from .api_1_0.errors import unauthorized


def permission_required(permission):
    """Check if a user has a permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Check if the user is an admin."""
    return permission_required(Permission.ADMINISTER)(f)


def requires_auth(f):
    """Check login using basic http authorization."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return unauthorized('Basic HTTP Auth Required')
        user = Brewer.query.filter_by(username=auth.username).first()
        if user is not None and user.verify_password(auth.password):
            return f(*args, **kwargs)
        return unauthorized('Invalid Credentials')
    return decorated
