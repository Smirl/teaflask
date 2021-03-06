"""Forms for tea input."""

from ..models import Tea, Role, Brewer
from flask.ext.wtf import Form
from flask.ext.pagedown.fields import PageDownField
from wtforms import StringField, SelectField, SubmitField, BooleanField, \
    TextAreaField, HiddenField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError


class PotForm(Form):

    """Brew a new pot of tea."""

    tea_id = SelectField('Tea', coerce=int)
    submit = SubmitField('Brew a pot')

    def __init__(self, *args, **kwargs):
        """Set the SelectField choices."""
        super(PotForm, self).__init__(*args, **kwargs)
        self.tea_id.choices = [(t.id, t.name) for t in Tea.query.all()]
        if not self.tea_id.choices:
            self.tea_id.choices = [(-1, 'No Teas available')]


class TeaForm(Form):

    """Add a new type of Tea."""

    name = StringField('Name of Tea', validators=[Required(), Length(1, 64)])
    category = StringField('Type of Tea', validators=[Required(), Length(1, 64)])
    location = StringField('Orign of Tea', validators=[Length(0, 64)])
    image_url = StringField('Image URL', validators=[Length(0, 256)])
    description = PageDownField("Description of Tea")
    brewing_methods = PageDownField("Brewing Method")
    tasting_notes = PageDownField("Tasting Notes")
    submit = SubmitField('Submit')


class EditProfileForm(Form):

    """Edit a user profile as that user."""

    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):

    """Edit a user profile as an admin."""

    id = HiddenField('id')
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[
        Required(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        """Set the roles to choose from."""
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = Brewer.query.get(self.id.data) if self.id.data else None

    def validate_email(self, field):
        """If email is changing make sure it is unique."""
        if ((self.user and field.data != self.user.email)
                and Brewer.query.filter_by(email=field.data).first()):
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        """If username is changing make sure it is unique."""
        if ((self.user and field.data) != self.user.username
                and Brewer.query.filter_by(username=field.data).first()):
            raise ValidationError('Username already in use.')
