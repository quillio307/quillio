from flask import Blueprint, jsonify
from flask_security import login_required, current_user

profile = Blueprint('profile', __name__)


@profile.route('/', methods=['GET'])
@login_required
def home():
    """ Displays information about the current user """

    user = current_user._get_current_object()

    friends = dict()
    topics = dict()

    for meeting in user.meetings:
        for member in meeting.members:
            if member == current_user._get_current_object():
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

    # determine best friends
    sorted_friends = sorted(friends, key=friends.get, reverse=True)

    # determine favorite topics
    sorted_topics = sorted(topics, key=topics.get, reverse=True)

    best_friends = dict()
    favorite_topics = dict()

    for i in range(0, 3):
        best_friends[i] = sorted_friends[i], friends[sorted_friends[i]]
        favorite_topics[i] = sorted_topics[i], topics[sorted_topics[i]]

    return jsonify({'Best Friends': best_friends, 'Favorite Topics': favorite_topics, 'Meeting Count': user.meeting_count})
