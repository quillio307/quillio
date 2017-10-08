from app import db

from flask_security import MongoEngineUserDatastore
from wtforms import Form, validators, StringField, PasswordField


class Note(db.Document):
    transcript = db.StringField()
    summary = db.StringField()
    recording = db.StringField()
