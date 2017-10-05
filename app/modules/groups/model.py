from wtforms import Form, validators
from wtforms import StringField

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


class GroupForm(Form):
    name = StringField('Meeting Name', [validators.Length(min=3, max=100),
                                        validators.DataRequired()])
    emails = StringField('Emails', [validators.DataRequired()])
    admin_emails = StringField('Admin Emails')
