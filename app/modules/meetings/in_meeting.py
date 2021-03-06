import json
import string
import time
import functools
import requests

from datetime import datetime, timedelta

from app import socketio
from app.modules.auth.model import User
from app.modules.meetings.model import Meeting, MeetingCreateForm, \
    MeetingUpdateForm, KeywordsForm

from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, jsonify, abort
from flask_security import current_user, login_required
from flask_socketio import SocketIO, emit, join_room, leave_room, send, rooms, disconnect
from flask_sendgrid import SendGrid
from app import app

meeting = Blueprint('meeting', __name__)


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@meeting.route('/<meeting_id>')
@login_required
def meeting_page(meeting_id):
    print("Receieved join request for: " + meeting_id)
    meeting = Meeting.objects.with_id(meeting_id)
    if meeting is None:
        abort(404)
        return
    if meeting.status() is 2:
        abort(400)
        return
    return render_template('meeting/in_meeting.html', meeting={'title': meeting.name, 'id': meeting_id})


@socketio.on('join', namespace='/meeting')
@authenticated_only
def on_join(data):
    user = current_user
    meeting = Meeting.objects.with_id(data['room_id'])
    if meeting is None:
        abort(404)
        return
    if meeting.status() is 2:
        abort(400)
    join_room(data['room_id'])
    emit('receivemsg', {'data': user.name + ' has joined the meeting.'}, room=data['room_id'])


@socketio.on('start', namespace='/meeting')
@authenticated_only
def start_meeting(data):
    meeting = Meeting.objects.with_id(data['room_id'])
    meeting.active = True
    meeting.save()
    emit('startMeeting', room=data['room_id'])

def update_grammar(meeting_id):
    meeting = Meeting.objects.with_id(meeting_id)
    transcriptCounter = 0
    transcripts = meeting.transcript
    print("holy SHIT fuck shit fuck")
    #text = "holy SHIT fuck shit fuck"
    #tool = language_check.LanguageTool('en-US')
    #matches = tool.check(text)
    #print(language_check.correct(text, matches)+" !!!!!!!!????!?!!?!?!?!??!!!!??!?!??!?!")
    for transcript in transcripts:
        r = requests.post('http://bark.phon.ioc.ee/punctuator',data={'text':transcript.transcription})
        print(r.text)
        meeting.transcript[transcriptCounter].transcription = r.text
        transcriptCounter = transcriptCounter + 1
    meeting.save()
    return


@socketio.on('end', namespace='/meeting')
@authenticated_only
def start_meeting(data):
    meeting = Meeting.objects.with_id(data['room_id'])
    meeting.active = False
    meeting.save()
    emit('endMeeting', room=data['room_id'])
    update_grammar(data['room_id'])
    pt = ""
    for ts in meeting.transcript:
        pt += '{0}: {1}\\n'.format(ts.user.name, ts.transcription)
    meeting.transcriptText = pt
    meeting.save()

    try:
        # send the password reset email
        for member in meeting.members:
            mail = SendGrid(app)
            mail.send_email(
                from_email=app.config['SENDGRID_DEFAULT_FROM'],
                to_email= member.email,
                subject='Quillio Meeting Completed',
                html=summary_html(member.name, meeting.name, meeting.get_summary())
            )
    except Exception as e:
        print(str(e))


@socketio.on('silenceAll', namespace='/meeting')
@authenticated_only
def silence_all(data):
    emit('silence', {}, room=data['room_id'], include_self=False)
    emit('receivemsg', {'data': data['user'] + " is talking."}, room=data['room_id'])


@socketio.on('leave', namespace='/meeting')
@authenticated_only
def on_leave(data):
    emit('receivemsg', {'data': current_user.name + ' has left the room.'}, room=data['room_id'])
    leave_room(data['room_id'])


@socketio.on('transcription', namespace='/meeting')
@authenticated_only
def transcription(data):
    usr = current_user._get_current_object()
    tscript = data['transcript']
    meeting = Meeting.objects.with_id(data['room_id'])
    if meeting.status() is 1:
        meeting.add_transcription(usr, tscript)
        meeting.save()
        emit('receivemsg', {'data': usr.name + ' - ' + tscript}, room=data['room_id'])


def summary_html(name, mname, summary):
    header = '<nav style="height:50px" class="navbar navbar-expand-lg pkColor"></nav><h2 align="center">Your Meeting Summary</h2>'
    body = '<p>Dear ' + name + ',</p><br><p> Your meeting ' + mname + ' has been completed. Here is a quick summary:</p>'

    ul = '<ul>'
    for s in summary:
        ul += '<li>'+s+'</li>'
    ul += '</ul>'
    close = '<p>Thanks!</p><br><p>The Quillio Team</p>'
    return header + body + ul + close
