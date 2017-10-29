import json
from flask import Flask, render_template, abort, request, request
import string
import time
from datetime import datetime, timedelta
from flask_socketio import SocketIO, emit, join_room, leave_room, send, rooms
from app import socketio
from app.modules.auth.model import User
from app.modules.meeting.model import Meeting, MeetingCreateForm, \
    MeetingUpdateForm
from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, jsonify
from flask_security import current_user, login_required


meeting = Blueprint('meeting', __name__)


@meeting.route('/meeting/<room_id>')
@login_required
def meeting_page(room_id):
    user = User.objects.with_id(user_id)
    meeting = Meeting.objects.with_id(room_id)
    if user is None or meeting is None:
        abort(404)

    return render_template('in_meeting.html', meeting={'title': meeting.name})


@socketio.on('join', namespace='/meeting')
def on_join(data):
    user = User.objects.with_id(data['user_id'])
    meeting = Meeting.objects.with_id(data['room_id'])
    if meeting.active is False:
        meeting.active = True
        meeting.save()
    join_room(data['room_id'])
    emit('receivemsg', {'data': data['user_id'] + ' has joined the meeting.'}, room=data['room_id'])


@socketio.on('start', namespace='/meeting')
def start_meeting(data):
    emit('startMeeting', room=data['room'])


@socketio.on('end', namespace='/meeting')
def start_meeting(data):
    emit('endMeeting', room=data['room'])


@socketio.on('silenceAll', namespace='/meeting')
def silence_all(data):
    emit('silence', {}, room=data['room'], include_self=False)
    emit('receivemsg', {'data': data['user'] + " is talking."}, room=data['room'])


@socketio.on('leave', namespace='/meeting')
def on_leave(data):
    username = data['username']
    room = data['room']
    emit('receivemsg', {'data':username + ' has left the room.'})
    leave_room(room)


@socketio.on('sendmsg', namespace='/meeting')
def test_message(message):
    username = message['username']
    room = message['room']
    emit('receivemsg', {'data': username+ ": " + message['data']}, room=room)


@socketio.on('connect', namespace='/meeting')
def test_connect():
    emit('my response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/meeting')
def test_disconnect():
    print('Client disconnected')