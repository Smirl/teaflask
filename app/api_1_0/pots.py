from flask import jsonify, request, g, url_for
from .. import db
from ..models import Pot, Permission, Brewer
from . import api, paginate
from .decorators import permission_required


@api.route('/pots/')
def get_pots():
    """Get a list of pots."""
    page = request.args.get('page', 1, type=int)
    pagination = paginate(Pot.query, page)
    pots = pagination.items
    _prev = None
    if pagination.has_prev:
        _prev = url_for('api.get_pots', page=page - 1, _external=True)
    _next = None
    if pagination.has_next:
        _next = url_for('api.get_pots', page=page + 1, _external=True)
    return jsonify({
        'pots': [pot.to_json() for pot in pots],
        'prev': _prev,
        'next': _next,
        'count': pagination.total,
    })


@api.route('/pots/<int:id>')
def get_pot(id):
    """Get a pot."""
    pot = Pot.query.get_or_404(id)
    return jsonify(pot.to_json())


@api.route('/pots/', methods=['POST'])
@permission_required(Permission.BREW)
def new_pot():
    """Create a new pot from json."""
    pot = Pot.from_json(request.json)
    pot.brewer = g.get('current_user', Brewer.query.get(1))
    db.session.add(pot)
    db.session.commit()
    return jsonify(pot.to_json()), 201, {
        'Location': url_for('api.get_pot', id=pot.id, _external=True)
    }
