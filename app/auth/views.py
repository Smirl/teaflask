"""Auth views for user management."""

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import Brewer
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm


@auth.before_app_request
def before_request():
    """Make sure users are confirmed."""
    if current_user.is_authenticated():
        current_user.ping()
        if not current_user.confirmed:
            flash('Your account is still unconfirmed.', 'warning')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login view."""
    form = LoginForm()
    if form.validate_on_submit():
        user = Brewer.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """Simple logout view."""
    logout_user()
    flash('You have been logged out.', 'warning')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Register as a new user."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Brewer(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            'Confirm Your Account',
            'auth/email/confirm',
            user=user,
            token=token
        )
        flash('A confirmation email has been sent to you by email.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/form.html', form=form, title='Register')


@auth.route('/test_email/')
def test_email():
    """Testing sending an email."""
    send_email(
        'alex.williams@skyscanner.net',
        'Test Email',
        'auth/email/confirm',
    )
    return 'Sent email'


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """Confirm an account."""
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!', 'info')
    else:
        flash('The confirmation link is invalid or has expired.', 'danger')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    """Send a confirmation email."""
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        'Confirm Your Account',
        'auth/email/confirm',
        user=current_user,
        token=token
    )
    flash('A new confirmation email has been sent to you by email.', 'info')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change the password if you are logged in."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.', 'info')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.', 'danger')
    return render_template("auth/form.html", form=form, title='Change Your Password')


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    """Ask to reset password if you have lost it."""
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = Brewer.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(
                user.email,
                'Reset Your Password',
                'auth/email/reset_password',
                user=user,
                token=token,
                next=request.args.get('next')
            )
        flash('An email with instructions to reset your password has been sent to you.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/form.html', form=form, title='Reset Your Password')


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """Change your password if you are resetting."""
    if not current_user.is_anonymous():
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = Brewer.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('You do not have permission to change this password.', 'danger')
            return redirect(url_for('main.index'))
    return render_template('auth/form.html', form=form, title='Reset Your Password')


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    """Change email handler."""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(
                new_email,
                'Confirm your email address',
                'auth/email/change_email',
                user=current_user,
                token=token
            )
            flash('An email with instructions to confirm your new email address has been sent to you.', 'info')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template("auth/form.html", form=form, title='Change Email Address')


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    """Change email if token is correct."""
    if current_user.change_email(token):
        flash('Your email address has been updated.', 'info')
    else:
        flash('Invalid request.', 'danger')
    return redirect(url_for('main.index'))
