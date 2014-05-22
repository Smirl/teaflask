"""Helper methods to send emails."""

from threading import Thread
from flask import current_app, render_template
from flask.ext.mail import Message
from . import mail


def send_async_email(app, msg):
    """Target for thread."""
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    """Send the email."""
    print(to, subject, template, kwargs)
    app = current_app._get_current_object()
    msg = Message(
        app.config['TEAFLASK_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
        sender=app.config['TEAFLASK_MAIL_SENDER'],
        recipients=[to]
    )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    print(msg, msg.body, msg.html)
    return mail.send(msg)
    # thr = Thread(target=send_async_email, args=[app, msg])
    # thr.start()
    # print('Thread started')
    # return thr
