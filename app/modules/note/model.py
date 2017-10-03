from flask_security import MongoEngineUserDatastore
from wtforms import Form, validators
from wtforms import StringField, PasswordField

from app.setup import db

class Note(db.Document):
    transcript = db.StringField(min_length=100)
    summary = db.StringField()
    recording = db.StringField()


