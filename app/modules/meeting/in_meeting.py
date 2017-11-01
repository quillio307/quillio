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


@meeting.route('/<meeting_id>')
@login_required
def meeting_page(meeting_id):
    print("Receieved join request for: " + meeting_id)
    meeting = Meeting.objects.with_id(meeting_id)
    if meeting is None:
        abort(404)
        return

    return render_template('meeting/in_meeting.html', meeting={'title': meeting.name})


@socketio.on('join', namespace='/meeting')
@login_required
def on_join(data):
    user = current_user
    meeting = Meeting.objects.with_id(data['room_id'])
    if meeting.active is False:
        meeting.active = True
        meeting.save()
    join_room(data['room_id'])
    emit('receivemsg', {'data': user.name + ' has joined the meeting.'}, room=data['room_id'])


@socketio.on('start', namespace='/meeting')
@login_required
def start_meeting(data):
    emit('startMeeting', room=data['room'])


@socketio.on('end', namespace='/meeting')
@login_required
def start_meeting(data):
    emit('endMeeting', room=data['room'])


@socketio.on('silenceAll', namespace='/meeting')
@login_required
def silence_all(data):
    emit('silence', {}, room=data['room'], include_self=False)
    emit('receivemsg', {'data': data['user'] + " is talking."}, room=data['room'])


@socketio.on('leave', namespace='/meeting')
@login_required
def on_leave(data):
    username = data['username']
    room = data['room']
    emit('receivemsg', {'data': username + ' has left the room.'})
    leave_room(room)


@socketio.on('sendmsg', namespace='/meeting')
@login_required
def test_message(message):
    username = message['username']
    room = message['room']
    emit('receivemsg', {'data': username + ": " + message['data']}, room=room)


@socketio.on('connect', namespace='/meeting')
@login_required
def test_connect():
    emit('my response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/meeting')
@login_required
def test_disconnect():
    print('Client disconnected')
