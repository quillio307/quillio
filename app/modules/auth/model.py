from app import app, db

from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin
from wtforms import Form, StringField, PasswordField, validators




class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    meta = {'strict': False}

    # identity fields
    email = db.EmailField(required=True, unique=True,
                          min_length=3, max_length=35)
    name = db.StringField(required=True, min_length=4, max_length=20)
    password = db.StringField(required=True, min_length=5, max_length=1000)

    # quillio fields
    groups = db.ListField(db.ReferenceField('Group'), default=[])
    meetings = db.ListField(db.ReferenceField('Meeting'), default=[])

    # authentication fields
    activation_hash = db.StringField()
    password_reset_hash = db.StringField()

    # security fields
    active = db.BooleanField(default=False)
    authenticated = db.BooleanField(default=False)
    roles = db.ListField(db.ReferenceField(Role), default=[])

    # statistics fields
    meeting_count = db.IntField(default=0)

    def is_authenticated(self):
        """ Determines if a User is authenticated """
        return self['authenticated']

    def is_active(self):
        """ Determines if a User is currently active """
        return self['active']

    def is_anonymous(self):
        """ Determines if a User is anonymous; this will always return false
        becuase anonymous users are not currently supported """
        return False

    def get_id(self):
        """ Fetches the unicode id for the User """
        return str(User.objects.get(email=self['email']).id)

    def get_stats(self):
        """ Determines the members who have the most meetings with the current
        user """
        friends = dict()
        topics = dict()

        for meeting in self.meetings:
            for member in meeting.members:
                if member == self:
                    pass
                elif member.name in friends:
                    friends[member.name] = friends[member.name] + 1
                else:
                    friends[member.name] = 1

            for topic in meeting.topics:
                if topic in topics:
                    topics[topic] = topics[topic] + 1
                else:
                    topics[topic] = 1
        
        sorted_friends = sorted(friends, key=friends.get, reverse=True)
        sorted_topics = sorted(topics, key=topics.get, reverse=True)

        best_friends = []
        favorite_topics = []
        for i in range(0, 3):
            if len(sorted_friends) > i:
                best_friends.append({
                    "name": sorted_friends[i],
                    "count": friends[sorted_friends[i]]
                })
            if len(sorted_topics) > i:
                favorite_topics.append({
                    "name": sorted_topics[i],
                    "count": topics[sorted_topics[i]]
                })
        
        result = dict()
        result['members'] = best_friends 
        result['topics'] = favorite_topics 
        return result


class SignupForm(Form):
    email = StringField('Email', [validators.DataRequired(),
                                  validators.Length(min=6, max=35)])
    name = StringField('Name', [validators.DataRequired(),
                                validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.Length(min=5, max=35)])


class LoginForm(Form):
    email = StringField('Email', [validators.DataRequired(),
                                  validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.Length(min=5, max=35)])


class PasswordResetRequestForm(Form):
    email = StringField('Email', [validators.DataRequired(),
                                  validators.Length(min=4)])


class PasswordResetForm(Form):
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.Length(min=5, max=35)])


# Flask-Security Setup
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Authentication Setup
# mail = SendGrid(app)
