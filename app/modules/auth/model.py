from app import app, db

from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin
from flask_sendgrid import SendGrid
from wtforms import Form, StringField, PasswordField, validators


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    meta = {'strict': False}

    # identity fields
    email = db.EmailField(required=True, unique=True,
                          min_length=3, max_length=35)
    name = db.StringField(required=True, min_length=4, max_length=20)
    password = db.StringField(required=True, min_length=5, max_length=1000)

    # quillio fields
    groups = db.ListField(db.ReferenceField('Group'), default=[])
    meetings = db.ListField(db.ReferenceField('Meeting'), default=[])

    # registration fields
    password_reset_hash = db.StringField(required=False)
    activation_hash = db.StringField(required=True)

    # security fields
    active = db.BooleanField(default=False)
    authenticated = db.BooleanField(required=False, default=False)
    roles = db.ListField(db.ReferenceField(Role), default=[])

    def is_authenticated(self):
        """ Determines if a User is authenticated """
        return self['authenticated']

    def is_active(self):
        """ Determines if a User is currently active """
        return self['active']

    def is_anonymous(self):
        """ Determines if a User is anonymous; this will always return false
        becuase anonymous users are not currently supported """
        return False

    def get_id(self):
        """ Fetches the unicode id for the Usera """
        # return str(User.objects(email__exact=self['email'])[0].id)
        return str(User.objects.get(email=self['email']).id)


# Flask-Security Setup
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Email Confirmation Setup
mail = SendGrid(app)


class SignupForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=35)])
    name = StringField('Name', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.Length(min=5, max=35)])


class LoginForm(Form):
    email = StringField('Email', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])

class PasswordReset(Form):
    email = StringField('Email', [validators.Length(min=4)])
