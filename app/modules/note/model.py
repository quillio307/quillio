from app import db
from app.modules.auth.model import User


class Transcription(db.Document):
    user = db.ReferenceField(User)
    transcription = db.StringField()


class Note(db.Document):
    transcript = db.ListField(db.ReferenceField(Transcription), default=[])
    summary = db.StringField()
    recording = db.StringField()

    def add_transcription(self, user, transcription):
        self.transcript.append(Transcription(user, transcription))
