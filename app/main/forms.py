"""Forms for tea input."""

from ..models import Tea, Role, Brewer
from flask.ext.wtf import Form
from flask.ext.pagedown.fields import PageDownField
from wtforms import StringField, SelectField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError


class PotForm(Form):

    """Brew a new pot of tea."""

    tea = SelectField('Tea', coerce=int)
    submit = SubmitField('Brew a pot')

    def __init__(self, *args, **kwargs):
        """Set the SelectField choices."""
        super(PotForm, self).__init__(*args, **kwargs)
        self.tea.choices = [(t.id, t.name) for t in Tea.query.all()]
        if not self.tea.choices:
            self.tea.choices = [(-1, 'No Teas available')]


class TeaForm(Form):

    """Add a new type of Tea."""

    name = StringField('Name of Tea', validators=[Required(), Length(1, 64)])
    category = StringField('Type of Tea', validators=[Required(), Length(1, 64)])
    location = StringField('Orign of Tea', validators=[Length(0, 64)])
    description = PageDownField("Description of Tea")
    brewing_methods = PageDownField("Brewing Method")
    tasting_notes = PageDownField("Tasting Notes")
    submit = SubmitField('Submit')

    def validate_name(self, field):
        """Tea name must be unique."""
        if Tea.query.filter_by(name=field.data).first():
            raise ValidationError('Tea already in database.')


class EditProfileForm(Form):

    """Edit a user profile as that user."""

    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):

    """Edit a user profile as an admin."""

    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        Required(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        """Set the roles to choose from."""
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        """If email is changing make sure it is unique."""
        if field.data != self.user.email and Brewer.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        """If username is changing make sure it is unique."""
        if field.data != self.user.username and Brewer.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
