from mongoengine import *
from flask_security import MongoEngineUserDatastore
from wtforms import Form, validators
from wtforms import StringField, PasswordField

from app.setup import db
from app.modules.auth.model import User
from app.modules.note.model import Note

class Meeting(db.Document):
    name = db.StringField(required=True, min_length=3, max_length=50) #title for meeting
    owner_id = db.ReferenceField(User) #connect to user object (whoever created the meeting)
    meeting_data = db.ReferenceField(Note) #connect to corresponding note object



class MeetingForm(Form):
    name = StringField('Meeting Name', [validators.Length(min=3, max=50), validators.DataRequired()])
    members = ListField(EmailField('Email Addresses', [validators.DataRequired()]))
