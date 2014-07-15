from flask import jsonify, request, url_for
from .. import db
from ..models import Pot, Permission, Tea
from . import api, paginate
from .decorators import permission_required


@api.route('/teas/')
def get_teas():
    page = request.args.get('page', 1, type=int)
    pagination = paginate(Tea.query.order_by(Tea.id.desc()), page)
    teas = pagination.items
    _prev = None
    if pagination.has_prev:
        _prev = url_for('api.get_teas', page=page - 1, _external=True)
    _next = None
    if pagination.has_next:
        _next = url_for('api.get_teas', page=page + 1, _external=True)
    return jsonify({
        'teas': [tea.to_json() for tea in teas],
        'prev': _prev,
        'next': _next,
        'count': pagination.total
    })


@api.route('/teas/<int:id>')
def get_tea(id):
    tea = Tea.query.get_or_404(id)
    return jsonify(tea.to_json())


@api.route('/teas/<int:id>/pots/')
def get_tea_pots(id):
    """Get the pots brewed for a tea."""
    tea = Tea.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = paginate(tea.pots.order_by(Pot.brewed_at.desc()), page)
    pots = pagination.items
    _prev = None
    if pagination.has_prev:
        _prev = url_for('api.get_tea_pots', id=id, page=page - 1, _external=True)
    _next = None
    if pagination.has_next:
        _next = url_for('api.get_tea_pots', id=id, page=page + 1, _external=True)
    return jsonify({
        'pots': [pot.to_json() for pot in pots],
        'prev': _prev,
        'next': _next,
        'count': pagination.total
    })


@api.route('/teas/', methods=['POST'])
@permission_required(Permission.BREW)
def new_tea():
    """Create a new tea from the json."""
    tea = Tea.from_json(request.json)
    db.session.add(tea)
    db.session.commit()
    return jsonify(tea.to_json()), 201, {
        'Location': url_for('api.get_tea', id=tea.id, _external=True)
    }
