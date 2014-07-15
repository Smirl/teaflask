from flask import jsonify, request, url_for
from . import api, paginate
from ..models import Brewer, Pot, Role


@api.route('/brewers/')
def get_brewers():
    """All brewers."""
    page = request.args.get('page', 1, type=int)
    pagination = paginate(Brewer.query, page)
    brewers = pagination.items
    _prev = None
    if pagination.has_prev:
        _prev = url_for('api.get_brewers', page=page - 1, _external=True)
    _next = None
    if pagination.has_next:
        _next = url_for('api.get_brewers', page=page + 1, _external=True)
    return jsonify({
        'brewers': [brewer.to_json() for brewer in brewers],
        'prev': _prev,
        'next': _next,
        'count': pagination.total,
    })


@api.route('/brewers/<int:id>/')
def get_brewer(id):
    """Get a single brewer."""
    brewer = Brewer.query.get_or_404(id)
    return jsonify(brewer.to_json())


@api.route('/brewers/<int:id>/pots/')
def get_brewer_pots(id):
    """Get the pots brewed by a brewer."""
    brewer = Brewer.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = paginate(brewer.pots.order_by(Pot.brewed_at.desc()), page)
    pots = pagination.items
    _prev = None
    if pagination.has_prev:
        _prev = url_for('api.get_brewer_pots', id=id, page=page - 1, _external=True)
    _next = None
    if pagination.has_next:
        _next = url_for('api.get_brewer_pots', id=id, page=page + 1, _external=True)
    return jsonify({
        'pots': [pot.to_json() for pot in pots],
        'prev': _prev,
        'next': _next,
        'count': pagination.total
    })


@api.route('/roles/')
def get_roles():
    """Get all of the roles."""
    return jsonify({
        'roles': [role.to_json() for role in Role.query.all()],
        'count': Role.query.count(),
    })


@api.route('/roles/<int:id>/')
def get_role(id):
    """Get a single role."""
    role = Role.query.get_or_404(id)
    return jsonify(role.to_json())


@api.route('/roles/<int:id>/brewers/')
def get_role_brewers(id):
    """Get the brewers for a role."""
    role = Role.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = paginate(role.brewers.order_by(Brewer.member_since.desc()), page)
    brewers = pagination.items
    _prev = None
    if pagination.has_prev:
        _prev = url_for('api.get_role_brewers', id=id, page=page - 1, _external=True)
    _next = None
    if pagination.has_next:
        _next = url_for('api.get_role_brewers', id=id, page=page + 1, _external=True)
    return jsonify({
        'brewers': [brewer.to_json() for brewer in brewers],
        'prev': _prev,
        'next': _next,
        'count': pagination.total,
    })
