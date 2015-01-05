from flask import jsonify, request, url_for
from .. import db
from ..models import Pot, Permission, Tea
from . import api, api_paginate, api_create, api_get
from .decorators import permission_required


@api.route('/teas/')
def get_teas():
    return api_paginate(
        'api.get_teas',
        Tea.query.order_by(Tea.id.desc()),
        tag_name='teas'
    )


@api.route('/teas/<int:id_>')
def get_tea(id_):
    return api_get(Tea, id_)


@api.route('/teas/<int:id_>/pots/')
def get_tea_pots(id_):
    """Get the pots brewed for a tea."""
    tea = Tea.query.get_or_404(id_)
    return api_paginate(
        'api.get_tea_pots',
        tea.pots.order_by(Pot.brewed_at.desc()),
        tag_name='pots',
        id_=id_
    )


@api.route('/teas/', methods=['POST'])
@permission_required(Permission.BREW)
def new_tea():
    """Create a new tea from the json."""
    return api_create(Tea)
