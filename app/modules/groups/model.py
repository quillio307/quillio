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
    meta = {'strict': False}

    def user_is_admin(self, user):
        """ Determines if a User is authenticated """
        if user in self.admins:
            return True
        return False

    def get_member_contributions(self):
        contribution = dict()
        for m in self.meetings:
            mContr = m.get_contr()
            contribution = {k: contribution.get(k, 0) + mContr.get(k, 0)
                            for k in set(contribution) | set(mContr)}
        return contribution

    def get_frequent_tags(self):
        tag_dict = dict()
        for m in self.meetings:
            for t in m.tags:
                tag_dict[t] = tag_dict.get(t, 0) + 1
        return tag_dict

    def get_frequent_topics(self):
        topic_dict = dict()
        for m in self.meetings:
            for t in m.topics:
                topic_dict[t] = topic_dict.get(t, 0) + 1
        return topic_dict


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
