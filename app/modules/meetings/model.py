from app import db
from datetime import datetime as dt

from app.modules.auth.model import User

from wtforms import Form, validators, StringField


class Transcription(db.EmbeddedDocument):
    user = db.ReferenceField(User)
    transcription = db.StringField()


class Meeting(db.Document):
    owner = db.ReferenceField(User, required=True)
    name = db.StringField(required=True, min_length=3, max_length=50)
    members = db.ListField(db.ReferenceField(User))
    active = db.BooleanField(default=False)
    tags = db.ListField(db.StringField(min_length=0, max_length=1000))
    topics = db.ListField(db.StringField(min_length=1, max_length=1000))
    objectives = db.ListField(db.StringField(min_length=1, max_length=1000))
    created_at = db.DateTimeField(default=dt.now())
    created_at_str = db.StringField(default=dt.now().strftime('%m-%d-%Y'))
    transcript = db.ListField(db.EmbeddedDocumentField(Transcription))
    summary = db.StringField()
    recording = db.StringField()
    transcriptText = db.StringField()
    meta = {'strict': False}

    def is_in_meeting(self, user):
        """ Determines if a User is allowed in this meeting """
        if user in self.members:
            return True
        return False

    def status(self):
        if self.active is True:
            return 1  # Active
        if not self.transcript:
            return 0  # Not started
        else:
            return 2  # Completed

    def add_transcription(self, user, transcription):
        self.transcript.append(Transcription(user, transcription))

    def get_contr(self):
        try:
            word_count = {}
            for t in self.transcript:
                if t.user.name in word_count:
                    word_count[t.user.name] = word_count[t.user.name] + len(t.transcript.split(" "))
                else:
                    word_count[t.user.name] = len(t.transcript.split(" "))
            return word_count
        except Exception as e:
            flash('error An Error Occured')
            return


class MeetingCreateForm(Form):
    name = StringField('Meeting Name', [validators.Length(min=3, max=100),
                                        validators.DataRequired()])
    emails = StringField('Emails', [validators.DataRequired()])


class MeetingUpdateForm(Form):
    meeting_id = StringField('Meeting ID')
    name = StringField('Name', [validators.Length(min=3, max=100),
                                validators.DataRequired()])
    emails_to_add = StringField('Users to Add')
    emails_to_remove = StringField('Users to Remove')


class MeetingDeleteForm(Form):
    meeting_id = StringField('Meeting ID', [validators.Required()])


class KeywordsForm(Form):
    keywords = StringField('Keywords', [validators.Required()])
    objectives = StringField('Objectives', [validators.Required()])
