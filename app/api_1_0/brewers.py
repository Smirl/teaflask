from . import api, api_paginate, api_get
from ..models import Brewer, Pot, Role


@api.route('/brewers/')
def get_brewers():
    """All brewers."""
    return api_paginate(
        'api.get_brewers',
        Brewer.query,
        tag_name='brewers'
    )


@api.route('/brewers/<int:id_>/')
def get_brewer(id_):
    """Get a single brewer."""
    return api_get(Brewer, id_)


@api.route('/brewers/<int:id_>/pots/')
def get_brewer_pots(id_):
    """Get the pots brewed by a brewer."""
    brewer = Brewer.query.get_or_404(id_)
    return api_paginate(
        'api.get_brewer_pots',
        brewer.pots.order_by(Pot.brewed_at.desc()),
        tag_name='pots'
    )


@api.route('/roles/')
def get_roles():
    """Get all of the roles."""
    return api_paginate('api.get_roles', Role.query, tag_name='roles')


@api.route('/roles/<int:id_>/')
def get_role(id_):
    """Get a single role."""
    return api_get(Role, id_)


@api.route('/roles/<int:id_>/brewers/')
def get_role_brewers(id_):
    """Get the brewers for a role."""
    role = Role.query.get_or_404(id_)
    return api_paginate(
        'api.get_role_brewers',
        role.brewers.order_by(Brewer.member_since.desc()),
        tag_name='brewers'
    )
