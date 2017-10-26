from app import app, db

from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin
from wtforms import Form, StringField, PasswordField, validators


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    email = db.EmailField(required=True, unique=True,
                          min_length=3, max_length=35)
    name = db.StringField(required=True, min_length=4, max_length=20)
    password = db.StringField(required=True, min_length=5, max_length=1000)
    password_reset_hash = db.StringField(required=False)
    active = db.BooleanField(default=False)
    activation_hash = db.StringField(required=True)
    authenticated = db.BooleanField(required=False, default=False)
    roles = db.ListField(db.ReferenceField(Role), default=[])
    groups = db.ListField(db.ReferenceField('Group'), default=[])
    meetings = db.ListField(db.ReferenceField('Meeting'), default=[])
    meta = {'strict': False}

    def is_authenticated(self):
        """ Determines if a User is authenticated """
        return self['authenticated']

    def is_active(self):
        """ Determines if a User is currently active """
        return self['active']

    # NOTE: always returns false, anonymous users are not supported
    def is_anonymous(self):
        """ Determines if a User is anonymous; this will always return false
        becuase this functionality is not currently supported """
        return False

    def get_id(self):
        """ Fetches the unicode id for the Usera """
        return str(User.objects(email__exact=self['email'])[0].id)


# Flask-Security Setup
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)


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
