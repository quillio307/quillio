from flask_security import MongoEngineUserDatastore, UserMixin, RoleMixin
from wtforms import Form, validators
from wtforms import StringField, PasswordField

from app.setup import db


class Role(db.Document, RoleMixin):
    """ Definition for a Role Document needed by Flask Security """
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    """ Definition for a User """
    email = db.EmailField(required=True, unique=True,
                          min_length=3, max_length=35)
    name = db.StringField(required=True, min_length=4, max_length=20)
    password = db.StringField(required=True, min_length=5, max_length=100)
    active = db.BooleanField(default=True)
    authenticated = db.BooleanField(required=False, default=False)
    roles = db.ListField(db.ReferenceField(Role), default=[])

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


user_datastore = MongoEngineUserDatastore(db, User, Role)


class SignupForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=35)])
    name = StringField('Name', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])


class LoginForm(Form):
    email = StringField('Email', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])
