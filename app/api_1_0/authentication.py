from flask import g, request
from ..models import Brewer, AnonymousBrewer
from . import api
from datetime import datetime, timedelta
from .errors import unauthorized, forbidden


@api.before_request
def before_request():
    # if current_app.config.get('DEBUG', False):
    #     return
    if not g.get('current_user') or (g.current_user and datetime.utcnow() > g.login_expires):
        auth = request.authorization
        if auth is None:
            return forbidden('Use Basic HTTP Auth')
        user = Brewer.query.filter_by(username=auth.username).first()
        if not user:
            g.user = AnonymousBrewer()
            return forbidden('Invalid username')
        if not user.verify_password(auth.password):
            g.user = AnonymousBrewer()
            return unauthorized('Invalid Credentials')
        g.current_user = user
        g.login_expires = datetime.utcnow() + timedelta(hours=1)
