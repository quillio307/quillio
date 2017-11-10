from app import app, db
#from app.modules.auth.model import User

class Pair(db.Document):
    user_one = db.ReferenceField('User')
    user_two = db.ReferenceField('User')
    meeting_count = db.IntField(default=1)



