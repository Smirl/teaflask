#!/usr/bin/env python

"""Django like manage.py ."""

import os
from app import create_app, db
from app.models import Pot, Brewer, Tea, Permission
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    """Create shell variables."""
    return dict(
        app=app,
        db=db,
        Permission=Permission,
        Pot=Pot,
        Brewer=Brewer,
        Tea=Tea,
    )
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    from subprocess import call
    args = [
        'nosetests',
        'app',
        '--with-coverage',
        '--cover-package=app',
        '--cover-html',
        '--cover-inclusive',
    ]
    call(args)


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app,
        restrictions=[length],
        profile_dir=profile_dir
    )
    app.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    from app.models import Role  # , User

    # migrate database to latest revision
    upgrade()

    # create user roles
    Role.insert_roles()

    # create self-follows for all users
    # User.add_self_follows()


if __name__ == '__main__':
    manager.run()
