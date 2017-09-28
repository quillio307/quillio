from app.setup import db
from app.modules.auth.model import User


class Group(db.Document):
    """ Definition for a Role Document needed by Flask Security """
    name = db.StringField(max_length=80, unique=True)
    members = db.ListField(field=db.ReferenceField(User), default=[])
    admins = db.ListField(field=db.ReferenceField(User), default=[])