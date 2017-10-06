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
        if user in self.admins:
            return True
        return False


class GroupCreateForm(Form):
    name = StringField('Meeting Name', [validators.Length(min=3, max=100),
                                        validators.DataRequired()])
    emails = StringField('Emails', [validators.DataRequired()])


class GroupSearchForm(Form):
    criteria = StringField('Criteria')


class GroupUpdateForm(Form):
    group_id = StringField('Group ID')
    name = StringField('Name')
    add_emails = StringField('Add Users')
    add_admin_emails = StringField('Add Admins')
    del_emails = StringField('Remove Users')
    description = StringField('Description')
