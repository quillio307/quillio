from app import db

from app.modules.auth.model import User
from app.modules.meetings.model import Meeting

from wtforms import Form, validators
from wtforms import StringField


class Group(db.Document):
    """ Definition for a Role Document needed by Flask Security """
    name = db.StringField(max_length=80)
    members = db.ListField(field=db.ReferenceField(User), default=[])
    admins = db.ListField(field=db.ReferenceField(User), default=[])
    meetings = db.ListField(db.ReferenceField(Meeting))
    contr = db.DictField()
    meta = {'strict': False}

    def user_is_admin(self, user):
        """ Determines if a User is authenticated """
        if user in self.admins:
            return True
        return False

    def update_contr(self):
        for m in meetings:
            mdict = m.get_contr
            self.contr = dict(self.contr.items() + mdict.items() +
                    [(k, self.contr[k] + mdict[k])
                    for k in set(self.contr) & set(mdict)])
        self.save()
        return


class GroupCreateForm(Form):
    name = StringField('Meeting Name', [validators.Length(min=3, max=100),
                                        validators.DataRequired()])
    emails = StringField('Emails', [validators.DataRequired()])


class GroupUpdateForm(Form):
    group_id = StringField('Group ID')
    name = StringField('Name')
    emails_to_add = StringField('Users to Add')
    admin_emails_to_add = StringField('Admins to Add')
    emails_to_remove = StringField('Users to Remove')
    description = StringField('Description')
    criteria = StringField('Criteria')


class GroupDeleteForm(Form):
    group_id = StringField('Group ID', [validators.DataRequired()])


class GroupSearchForm(Form):
    criteria = StringField('Criteria')
