"""Useful decorators for the app."""

from functools import wraps
from flask import abort, flash, redirect, render_template
from flask.ext.login import current_user
from .models import Permission
from . import db


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


def add_or_edit_view(model, form_type, template, *, task=None, id_=None, messages=None):
    """A helper to create or edit a model instance."""
    def _edited(obj):
        return '{} has been edited.'.format(str(obj))

    def _added(obj):
        return '{} has been added.'.format(str(obj))
    messages = messages if messages else (_added, _edited)

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            obj = model.query.get_or_404(id_) if task == 'edit' else model()
            form = form_type()
            if form.validate_on_submit():
                form.populate_obj(obj)
                db.session.add(obj)
                db.session.commit()
                if task == 'new':
                    flash(messages[0](obj), 'info')
                    return redirect(model.get_url(id_))
                flash(messages[1](obj), 'info')

            if not form.is_submitted():
                form.process(obj=obj)

            return render_template(template, form=form)
        return wrapper
    return decorate
