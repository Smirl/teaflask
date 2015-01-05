from flask import Blueprint, request, current_app, url_for, jsonify
from .. import db

api = Blueprint('api', __name__)


def api_paginate(endpoint, query, *, tag_name='results', **kwargs):
    """Helper for any paginated list of results."""
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(
        page,
        per_page=request.args.get(
            'limit',
            current_app.config['TEAFLASK_PER_PAGE'],
            type=int
        ),
        error_out=False
    )
    _prev = None
    if pagination.has_prev:
        _prev = url_for(endpoint, page=page - 1, _external=True, **kwargs)
    _next = None
    if pagination.has_next:
        _next = url_for(endpoint, page=page + 1, _external=True, **kwargs)
    return jsonify({
        tag_name: [item.to_json() for item in pagination.items],
        'prev': _prev,
        'next': _next,
        'count': pagination.total
    })


def api_create(model, **kwargs):
    """A helper for a POST method to create a new model."""
    if not request.json:
        from .errors import bad_request
        return bad_request('Empty POST body')

    obj = model.from_json(request.json)
    for name, value in kwargs.items():
        setattr(obj, name, value)
    db.session.add(obj)
    db.session.commit()

    endpoint = 'api.get_' + model.__name__.lower()
    return jsonify(obj.to_json()), 201, {
        'Location': url_for(endpoint, id=obj.id, _external=True)
    }


def api_get(model, id_):
    """A helper to return the json of a single model instance."""
    obj = model.query.get_or_404(id_)
    return jsonify(obj.to_json())

# Must be below the other code
from . import authentication, pots, brewers, teas, errors
