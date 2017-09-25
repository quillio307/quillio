import wtforms
# from wtforms import Form, StringField, EmailField, BooleanField
from mongoengine import Document, connect
from mongoengine import StringField, EmailField, BooleanField

from config import MONGODB_SETTINGS

connect(MONGODB_SETTINGS['db'], host=MONGODB_SETTINGS['host'])


class User(Document):
    """ Definition for the User document. """
    name = StringField(required=True, min_length=2, max_length=50)
    email = EmailField(required=True, min_length=5, unique=True)
    username = StringField(required=True, min_length=3, max_length=20)
    password = StringField(required=True, min_length=6, max_length=35)
    authenticated = BooleanField(required=False, default=False)

    def is_authenticated(self):
        """ Determines if a User is authenticated """
        return self['authenticated']

    # always returns true since we dont have emailing activation services yet
    def is_active(self):
        """ Determines if a User is currently active """
        return False

    # will always return false, this is not supported
    def is_anonymous(self):
        """ Determines if a User is anonymous; this will always return false
        becuase this functionality is not currently supported """
        return False

    def get_id(self):
        """ Fetches the unicode id for the User """
        return chr(User.objects(email__exact=self['email'])[0]._id)


class SignupForm(wtforms.Form):
    name = wtforms.StringField('Full Name', [wtforms.validators.Length(min=3, max=30)])
    email = wtforms.StringField('Email Address', [wtforms.validators.Length(min=6, max=35)])
    username = wtforms.StringField('Username', [wtforms.validators.Length(min=4, max=25)])
    password = wtforms.PasswordField('New Password', [
        wtforms.validators.DataRequired()
    ])
