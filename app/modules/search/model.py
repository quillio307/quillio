from flask_security import MongoEngineUserDatastore, UserMixin, RoleMixin
from wtforms import Form, validators
from wtforms import StringField, PasswordField

from app.setup import db

from app.modules.auth.model import User

class SearchForm(Form):
    email = StringField('Email', [validators.Length(min=6, max=35)])
