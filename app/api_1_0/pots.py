from flask import g
from ..models import Pot, Permission, Brewer
from . import api, api_paginate, api_create, api_get
from .decorators import permission_required


@api.route('/pots/')
def get_pots():
    """Get a list of pots."""
    return api_paginate('api.get_pots', Pot.query, tag_name='pots')


@api.route('/pots/<int:id_>')
def get_pot(id_):
    """Get a pot."""
    return api_get(Pot, id_)


@api.route('/pots/', methods=['POST'])
@permission_required(Permission.BREW)
def new_pot():
    """Create a new pot from json."""
    return api_create(Pot, brewer=g.get('current_user', Brewer.query.get(1)))
