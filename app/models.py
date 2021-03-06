"""Date models for the app include Pot, Tea, Brewer."""

from . import db, login_manager
from .exceptions import ValidationError
from flask import current_app, request, url_for
from flask.ext.login import AnonymousUserMixin, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import MultiDict
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
import hashlib


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class Pot(db.Model):

    """The class which represents a pot of tea that has been made."""

    __tablename__ = 'pots'

    id = db.Column(db.Integer, primary_key=True)
    brewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    drank_at = db.Column(db.DateTime, default=None)
    tea_id = db.Column(db.Integer, db.ForeignKey('teas.id'))
    brewer_id = db.Column(db.Integer, db.ForeignKey('brewers.id'))

    @property
    def drinkable(self):
        """If pot has not been drank."""
        return self.drank_at is None

    def __repr__(self):
        """String representation."""
        return '<Pot {} -{}>'.format(self.id, self.tea.name)

    def to_json(self):
        """Output the pot to a API format."""
        drank_at = self.drank_at.strftime(DATE_FORMAT) if self.drank_at else None
        return {
            'id': self.id,
            'url': Pot.get_url(self.id),
            'brewed_at': self.brewed_at.strftime(DATE_FORMAT),
            'drank_at': drank_at,
            'tea': Tea.get_url(self.tea_id),
            'tea_name': self.tea.name,
            'brewer': Brewer.get_url(self.brewer_id),
            'brewer_username': self.brewer.username,
        }

    @staticmethod
    def from_json(data):
        """Return a Pot from a json blob."""
        from app.main.forms import PotForm
        return from_json_helper(data, Pot, PotForm)

    @staticmethod
    def get_url(id_):
        """Return the URL for the object with the given id."""
        return url_for('api.get_pot', id_=id_, _external=True)


class Tea(db.Model):

    """Hold information about different types of tea."""

    __tablename__ = 'teas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    category = db.Column(db.String(64))
    location = db.Column(db.String(64))
    image_url = db.Column(db.String(256))
    description = db.Column(db.Text())
    brewing_methods = db.Column(db.Text())
    tasting_notes = db.Column(db.Text())
    pots = db.relationship('Pot', backref='tea', lazy='dynamic')

    def __repr__(self):
        """String representation."""
        return '<Tea {}>'.format(self.name)

    def to_json(self):
        """Output the tea to a API format."""
        return {
            'id': self.id,
            'url': Tea.get_url(self.id),
            'name': self.name,
            'category': self.category,
            'location': self.location,
            'image_url': self.image_url,
            'description': self.description,
            'brewing_methods': self.brewing_methods,
            'tasting_notes': self.tasting_notes,
            'pots': url_for('api.get_tea_pots', id_=self.id, _external=True),
        }

    @staticmethod
    def from_json(data):
        """Return a Pot from a json blob."""
        from app.main.forms import TeaForm
        return from_json_helper(data, Tea, TeaForm)

    @staticmethod
    def get_url(id_):
        """Return the URL for the object with the given id."""
        return url_for('api.get_tea', id_=id_, _external=True)


class Brewer(UserMixin, db.Model):

    """A user in the database which can brew pots of tea."""

    __tablename__ = 'brewers'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    pots = db.relationship('Pot', backref='brewer', lazy='dynamic')

    def __init__(self, **kwargs):
        """Set the role and avatar_hash."""
        super(Brewer, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        """Password is not readable."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Set the password as the hash."""
        self.password_hash = generate_password_hash(password)

    def get_name(self):
        """Get the real or user name."""
        return self.name or self.username

    def verify_password(self, password):
        """Helper to see if the password is correct."""
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        """Generate the confirm token."""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        """Change the confirmed if the token matches."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        """Generate the reset token."""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        """Change the password if the token matches."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        """Generate the email change token."""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        """Change the email if the token matches."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        """Help to check is user has permission."""
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        """Helper to check is user is Administrator."""
        return self.can(Permission.ADMINISTER)

    def ping(self):
        """Update the last_seen."""
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        """Get gravatar for the users email."""
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        _hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url,
            hash=_hash,
            size=size,
            default=default,
            rating=rating
        )

    def generate_auth_token(self, expiration):
        """Generate token for the user."""
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        """Get the user from token."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return Brewer.query.get(data['id'])

    def to_json(self):
        """Serialize to json."""
        return {
            'id': self.id,
            'url': Brewer.get_url(self.id),
            'email': self.email,
            'username': self.username,
            'role': self.role.name if self.role else None,
            'confirmed': self.confirmed,
            'name': self.name,
            'location': self.location,
            'about_me': self.about_me,
            'member_since': self.member_since.strftime(DATE_FORMAT),
            'last_seen': self.last_seen.strftime(DATE_FORMAT),
            'pots': url_for('api.get_brewer_pots', id_=self.id, _external=True),
        }

    @staticmethod
    def get_url(id_):
        """Return the URL for the object with the given id."""
        return url_for('api.get_brewer', id_=id_, _external=True)

    def __repr__(self):
        """String representation."""
        return '<Brewer %r>' % self.username


class AnonymousBrewer(AnonymousUserMixin):

    """Custom anonymous_user to create helper methods."""

    def can(self, permissions):
        """Help to check is user has permission."""
        return False

    def is_administrator(self):
        """Helper to check is user is Administrator."""
        return False

login_manager.anonymous_user = AnonymousBrewer


@login_manager.user_loader
def load_user(user_id):
    """Load the user from an id."""
    return Brewer.query.get(int(user_id))


class Permission:

    """Bit enum for permissions."""

    DRINK = 0x01
    BREW = 0x02
    MODERATE = 0x08
    ADMINISTER = 0x80


class Role(db.Model):

    """Manage permissions."""

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    brewers = db.relationship('Brewer', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        """Insert all of the roles into the database."""
        roles = {
            'User': Permission.DRINK | Permission.BREW,
            'Moderator': Permission.DRINK | Permission.BREW | Permission.MODERATE,
            'Administrator': 0xff,
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r]
            if r == 'User':
                role.default = True
            db.session.add(role)
        db.session.commit()

    def to_json(self):
        """The json repr of a Role."""
        return {
            'id': self.id,
            'url': url_for('api.get_role', id_=self.id, _external=True),
            'name': self.name,
            'default': self.default,
            'permissions': self.permissions,
            'brewers': url_for('api.get_role_brewers', id_=self.id, _external=True),
        }

    def __repr__(self):
        """String representation."""
        return '<Role %r>' % self.name


# ------------------------------------------------------------------------------
# HELPERS

def from_json_helper(data, model, form_class):
    """For a given MultiDict data, create a model using the repective form_class."""
    form = form_class(MultiDict(data), csrf_enabled=False)
    obj = model()
    if not form.validate():
        helper = {
            x[0]: list(x[1].args) + [y.__class__.__name__ for y in x[1].kwargs.get('validators', [])]
            for x in form._unbound_fields
            if x[0] not in ('csrf_token', 'submit')
        }
        raise ValidationError({
            'description': 'Data not given or invalid',
            'validation_errors': form.errors,
            'available_fields': helper,
        })
    form.populate_obj(obj)
    return obj
