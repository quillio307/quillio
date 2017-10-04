from app.setup import db
from app.modules.auth.model import User


class Group(db.Document):
    """ Definition for a Role Document needed by Flask Security """
    name = db.StringField(max_length=80)
    members = db.ListField(field=db.ReferenceField(User), default=[])
    admins = db.ListField(field=db.ReferenceField(User), default=[])
    meta = {'strict': False}

    def user_is_admin(self, user):
        """ Determines if a User is authenticated """
        for admin in self.admins:
            if admin == user:
                return True
        return False
