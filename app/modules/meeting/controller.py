import json, string, time

from datetime import datetime, timedelta
from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, jsonify
from flask_security import current_user, login_required

from app.modules.auth.model import User
from app.modules.meeting.model import Meeting, MeetingForm

from app.setup import db

meeting = Blueprint('meeting', __name__)


@meeting.route('/', methods=['GET', 'POST'])
@login_required
def home():
    form = MeetingForm(request.form)
    if request.method == 'GET':
        usr = current_user._get_current_object()
        res = []
        for meet in usr.meetings:
            res.append({'name': meet.name})
        return render_template('meeting.html', meetings=res, form=form)

    if form.validate():
        try:
            # generate list of users that will be in the meeting
            emails = form.emails.data.split(" ")
            emails.append(current_user.email)

            # grab the list of valid users
            query = User.objects(email__in=emails)
            query_emails = [u.email for u in query]

            # validate that all the members exist
            if len(emails) == len(query):
                # add the meeting to each user's meetings list
                m = Meeting(name=form.name.data,
                            members=query, active=True).save()
                for u in query:
                    u.meetings.append(m)
                    u.save()
                flash('New meeting created with member(s): {}'
                      .format(query_emails))
                return redirect(url_for('meeting.home'))
            # show the invalid users
            else:
                invalid = list(set(emails) - set(query_emails))
                flash('Could not find user(s): {}'.format(invalid))
                return redirect(url_for('meeting.home'))
        except Exception as e:
            flash('A problem has occurred, please try again! {}'.format(e))
            return redirect(url_for('meeting.home'))
    flash('Invalid input.  Please try again!')
    return redirect(url_for('meeting.home'))


@meeting.route('/active/<string:meeting_id>', methods=['GET'])
@login_required
def get_active_meeting(meeting_id):
    # validate meeting id
    if len(meeting_id) == 24 and all(c in string.hexdigits for c in meeting_id):
        query = Meeting.objects(id__exact=meeting_id)
        if len(query) > 0:
            # assert that the current user has access to the given meeting
            if current_user not in query[0].members:
                flash('You are not a member of that meeting.')
                return redirect(url_for('meeting.meetings_page'))
            return jsonify({'Meeting': query})
        else:
            flash('Meeting Not found')
            return redirect(url_for('meeting.meetings_page'))
    flash('Invalid Meeting Id.')
    return redirect(url_for('meeting.meetings_page'))


@meeting.route('/search/<string:date_from>/to/<string:date_to>')
@login_required
def search_date(date_from, date_to):
    start_time = datetime.strptime(date_from,'%b.%d.%Y')
    end_time = datetime.strptime(date_to, '%b.%d.%Y')
    end_time += timedelta(days=1)
    meetings = current_user.meetings
    filtered = list(filter(lambda x: x.created_at >= start_time and x.created_at <= end_time, meetings))
    return jsonify({'results': filtered})


@meeting.route('/search/<string:meeting_title>')
@login_required
def search(meeting_title):
    meetings = current_user.meetings
    filtered = list(filter(lambda x: x.name == meeting_title, meetings))
    return jsonify({'results': filtered})



@meeting.route('/all', methods=['GET'])
@login_required
def all_meetings():
    usr = current_user._get_current_object()
    res = []
    for meet in usr.meetings:
        res.append({'name': meet.name})
    return json.dumps(res)
