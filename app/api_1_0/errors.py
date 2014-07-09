"""API errors and handlers."""

from flask import jsonify
from . import api


def bad_request(message):
    """Bad request helper method."""
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    """Unauthorized helper method."""
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    """Forbidden helper method."""
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


class ValidationError(ValueError):

    """Custom error for validation."""

    pass


@api.errorhandler(ValidationError)
def validation_error(e):
    """Handle when a ValidationError is raised."""
    return bad_request(e.args[0])
