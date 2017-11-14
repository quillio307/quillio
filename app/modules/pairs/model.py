from app import db


class Pair(db.Document):
    user_one = db.ReferenceField('User')
    user_two = db.ReferenceField('User')
    meeting_count = db.IntField(default=1)
