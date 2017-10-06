from datetime import datetime as dt
from flask_security import MongoEngineUserDatastore
from wtforms import Form, validators
from wtforms import StringField

from app.setup import db
from app.modules.auth.model import User
from app.modules.note.model import Note


class Meeting(db.Document):
    owner = db.ReferenceField(User, required=True)
    name = db.StringField(required=True, min_length=3, max_length=50)
    members = db.ListField(db.ReferenceField(User))
    active = db.BooleanField()
    created_at_str = db.StringField(default=dt.now().strftime('%b %d %Y'))
    created_at = db.DateTimeField(default=dt.now())
    

class MeetingCreateForm(Form):
    name = StringField('Meeting Name', [validators.Length(min=3, max=100),
                                        validators.DataRequired()])
    emails = StringField('Emails', [validators.DataRequired()])


class MeetingSearchForm(Form):
    criteria = StringField('Criteria')
