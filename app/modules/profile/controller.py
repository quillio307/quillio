from flask import Blueprint, jsonify
from flask_security import login_required, current_user

profile = Blueprint('profile', __name__)


@profile.route('/', methods=['GET'])
@login_required
def home():
    """ Displays information about the current user """

    user = current_user._get_current_object()

    # generate count of meetings with each meeting member
    friends = dict()
    for meeting in user.meetings:
        for member in meeting.members:
            if member == current_user._get_current_object():
                pass
            elif member.name in friends:
                friends[member.name] = friends[member.name] + 1
            else:
                friends[member.name] = 1

    # determine best friends
    winners = sorted(friends, key=friends.get, reverse=True)

    best_friends = dict()

    for i in range(0, 3):
        best_friends[i] = winners[i], friends[winners[i]]

    return jsonify({'Best Friends': best_friends, 'Meeting Count': user.meeting_count})
