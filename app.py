"""
A simple flask app to see when tea is ready to drink in DA.

/ is the status screen.
/brewed/<tea_name> to add tea
/drank/ to say the last pot has been drank
/api/ for the json api
"""

import os
from datetime import datetime
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connect to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initialize the database."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """
    Open a new database connection.

    If there is none yet for the current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Close the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def home():
    """The main tea screen."""
    db = get_db()
    try:
        cur = db.execute('select datetime, tea, brewer, drinkable from pots order by id desc')
        date, tea, brewer, drinkable = cur.fetchone()
    except TypeError:
        date, tea, brewer, drinkable = None, None, None, False
    context = {
        'status': 'Tea is ready' if drinkable else 'No tea is ready.',
        'description': 'A fine pot of {} has been brewed.'.format(tea) if drinkable else '',
        'brewer': 'thanks {}'.format(brewer) if drinkable else '',
        'drinkable': drinkable,
        'logged_in': session.get('logged_in', False),
    }
    return render_template('index.html', **context)


@app.route('/brewed', methods=['GET', 'POST'])
def add_pot():
    """Add a pot of tea."""
    if request.method == 'POST':
        if not session.get('logged_in'):
            abort(401)
        db = get_db()
        db.execute(
            'insert into pots (datetime, tea, brewer, drinkable) values (?, ?, ?, ?)',
            [
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                request.form['tea'],
                request.form['brewer'],
                1,
            ]
        )
        db.commit()
        flash('New pot was successfully posted')
        return redirect(url_for('home'))
    return render_template('brewed.html')


@app.route('/drank')
def remove_pot():
    """Set the last pot as empty."""
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.execute('select datetime, tea, brewer, drinkable from pots order by id desc')
    date, tea, brewer, drinkable = cur.fetchone()
    if drinkable:
        db.execute(
            'insert into pots (datetime, tea, brewer, drinkable) values (?, ?, ?, ?)',
            [datetime.now().strftime('%Y-%m-%d %H:%M'), tea, brewer, 0]
        )
        db.commit()
        flash('Pot was successfully drank')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in to the system."""
    message = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            message = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            message = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('home'))
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    """Log out of the system."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))


@app.route('/api')
def api():
    """Used to test the template engine."""
    def get_distinct(col, table):
        """Get the list of distinct values."""
        if not request.args or request.args.get(col):
            cur = db.execute('select distinct {} from {}'.format(col, table))
            results[col] = [x[0] for x in cur.fetchall()]
            limit = int(request.args.get(col, 0))
            if limit > 0:
                results[col] = results[col][:limit]

    db = get_db()
    results = {}

    if not request.args or request.args.get('pots'):
        cur = db.execute('select datetime, tea, brewer from pots where drinkable = 1 order by id desc')
        results['pots'] = [dict(zip(x.keys(), list(x))) for x in cur.fetchall()]
        limit = int(request.args.get('pots', 0))
        if limit > 0:
            results['pots'] = results['pots'][:limit]

    for col in set(['brewer', 'tea']):
        get_distinct(col, 'pots')

    return jsonify(**results)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=False,
        port=5000
    )
