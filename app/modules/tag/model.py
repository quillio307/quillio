from app import db
from datetime import datetime as dt

from app.modules.meeting.model import Meeting

from flask_security import MongoEngineUserDatastore
from wtforms import Form, validators, StringField


class Tag(db.Document):
    string = db.StringField(required=True, min_length=1, max_length=50)
    meetings = db.ListField(db.ReferenceField(Meeting))
