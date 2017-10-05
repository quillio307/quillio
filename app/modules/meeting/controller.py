import string

from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, jsonify
from flask_security import current_user, login_required

from app.modules.auth.model import User
from app.modules.meeting.model import MeetingForm
from app.modules.meeting.model import Meeting
from app.modules.dash.controller import dash

from app.setup import db

meeting = Blueprint('meeting', __name__)


@meeting.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = MeetingForm(request.form)
    if request.method == 'GET':
        return render_template('meeting/create.html', form=form)

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
                m = Meeting(name=form.name.data, members=query, active=True).save()
                for u in query:
                    u.meetings.append(m)
                    u.save()
                flash('New meeting created with member(s): {}'
                      .format(query_emails))
                return redirect(url_for('dash.home'))
            # show the invalid users
            else:
                invalid = list(set(emails) - set(query_emails))
                flash('Could not find user(s): {}'.format(invalid))
                return redirect(url_for('meeting.create'))
        except Exception as e:
            flash('A problem has occurred, please try again! {}'.format(e))
            return redirect(url_for('meeting.create'))
    flash('Please list a meeting name between 3 and 50 characters in length!')
    return redirect(url_for('dash.home'))


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
                return redirect(url_for('dash.home'))
            return jsonify({'Meeting': query})
        else: 
            flash('Meeting Not found')
            return redirect(url_for('dash.home'))
    flash('Invalid Meeting Id.')
    return redirect(url_for('dash.home'))


@meeting.route('/search/<string:meeting_title>')
@login_required
def search(meeting_title):
    query = Meeting.objects(name__iexact=meeting_title)
    return jsonify({'results': query})


@meeting.route('/all', methods=['GET'])
@login_required
def all_meetings():
    usr = current_user._get_current_object()
    res = []
    for meet in usr.meeting:
        res.append({'name': meet.name, 'admin': meet.user_is_admin(usr)})
    return json.dumps(res)

@meeting.route('/', methods=['GET'])
@login_required
def meetings_page():
    usr = current_user._get_current_object()
    res = []
    for meet in usr.meeting:
        res.append({'name': meet.name, 'admin': meet.user_is_admin(usr)})
    return render_template('meeting.html', meeting=res)
