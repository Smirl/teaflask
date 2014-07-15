"""Helper methods to send emails."""

from threading import Thread
from flask import current_app, render_template, flash
from flask.ext.mail import Message
from . import mail


def send_async_email(app, msg):
    """Target for thread."""
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, *, async=False, **kwargs):
    """Send the email."""
    app = current_app._get_current_object()
    if app.config['MAIL_USERNAME'] is None or app.config['MAIL_PASSWORD'] is None:
        flash('Emails cannot be sent at this time. Please contact site admin.')
        return None
    msg = Message(
        app.config['TEAFLASK_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
        sender=app.config['TEAFLASK_MAIL_SENDER'],
        recipients=[to]
    )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    if async:
        thr = Thread(target=send_async_email, args=[app, msg])
        thr.start()
        return thr
    else:
        return mail.send(msg)
