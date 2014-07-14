"""Main tea related views."""

from . import main
from .. import db
from .forms import PotForm, TeaForm, EditProfileForm, EditProfileAdminForm
from ..models import Pot, Brewer, Tea, Role
from ..decorators import admin_required
from flask import render_template, flash, redirect, url_for
from flask.ext.login import current_user, login_required
from datetime import datetime
from sqlalchemy import func


@main.route('/')
def index():
    """The main tea screen."""
    pot = Pot.query.filter_by(drank_at=None).order_by(Pot.brewed_at.desc()).first()
    pots = Pot.query.order_by(Pot.brewed_at.desc()).limit(10)
    return render_template('main/index.html', pot=pot, pots=pots), 418


@main.route('/brew', methods=['GET', 'POST'])
@login_required
def brew():
    """Brew a pot of tea."""
    form = PotForm()
    if form.validate_on_submit():
        tea = Tea.query.get(form.tea.data)
        if not tea:
            flash('Not a valid tea', 'warning')
        else:
            pot = Pot(
                brewer=current_user._get_current_object(),
                tea=tea,
            )
            db.session.add(pot)
            flash('A pot of {} has been brewed.'.format(tea.name), 'info')
            return redirect(url_for('main.index'))
    teas = Tea.query.outerjoin(Pot).order_by(func.count(Tea.pots).desc()).group_by(Tea.id).all()
    return render_template('main/brewed.html', form=form, teas=teas)


@main.route('/tea/new', methods=['GET', 'POST'], defaults={'task': 'new', 'tea_id': None})
@main.route('/tea/edit/<tea_id>', methods=['GET', 'POST'], defaults={'task': 'edit'})
@login_required
def add_tea(task, tea_id):
    """Add a type of tea."""
    if task == 'edit':
        tea = Tea.query.get_or_404(tea_id)
    else:
        tea = Tea()

    form = TeaForm()
    if form.validate_on_submit():
        tea.__dict__.update(_get_cleaned_data(form))
        db.session.add(tea)
        if task == 'new':
            flash('{} has been added as a tea.'.format(tea.name), 'info')
            return redirect(url_for('main.tea', tea_id=tea.id))
        flash('{} has been edited.'.format(tea.name), 'info')

    if not form.is_submitted():
        form.process(obj=tea)

    return render_template('main/add_tea.html', form=form)


@main.route('/drink', defaults={'pot_id': None})
@main.route('/drink/<pot_id>')
def drink(pot_id):
    """Set the last pot as empty."""
    if pot_id:
        pot = Pot.query.get(pot_id)
        if not pot.drinkable:
            flash('This pot has already been drank', 'warning')
            return redirect(url_for('main.index'))
    else:
        pot = Pot.query.filter_by(drank_at=None).order_by(Pot.brewed_at.desc()).first()
    pot.drank_at = datetime.utcnow()
    db.session.add(pot)
    flash('The pot of {} brewed by {} has been drank'.format(pot.tea.name, pot.brewer.name), 'info')
    return redirect(url_for('main.index'))


@main.route('/tea/<tea_id>')
def tea(tea_id):
    tea = Tea.query.get_or_404(tea_id)
    form = PotForm()
    return render_template('main/tea.html', tea=tea, form=form)


@main.route('/user/<username>')
def user(username):
    user = Brewer.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.', 'info')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('auth/form.html', form=form, title='Edit your profile.')


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = Brewer.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.', 'info')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('auth/form.html', form=form, user=user, title='Edit a profile.')


# @main.route('/api')
# def api():
#     """Used to test the template engine."""
#     results = {}
#     results['pots'] = [
#         {'brewer': p.brewer.username, 'tea': p.tea.name, 'brewed_at': p.brewed_at} for p in Pot.query.limit(10)
#     ]
#     results['brewers'] = [b.username for b in Brewer.query.limit(10)]
#     results['teas'] = [t.name for t in Tea.query.limit(10)]

#     return jsonify(**results)


# ------------------------------------------------------------------------------
# HELPERS

def _get_cleaned_data(form, exclude=None, **kwargs):
    """
    Get the data to create a model from a form.

    Use exclude to list the string names of the fields to exclude. by default
    submit and csrf_token are removed.

    Use kwargs to update the returned dict.
    """
    _exclude = ['submit', 'csrf_token']
    if isinstance(exclude, list):
        _exclude.extend(exclude)

    cleaned_data = {k: v.data for k, v in form._fields.items()}
    for field in _exclude:
        cleaned_data.pop(field)

    cleaned_data.update(kwargs)
    return cleaned_data
