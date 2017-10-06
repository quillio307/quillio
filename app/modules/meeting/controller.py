import json, string, time

from datetime import datetime, timedelta
from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, jsonify
from flask_security import current_user, login_required


from app.modules.auth.model import User
from app.modules.meeting.model import Meeting, MeetingCreateForm, \
    MeetingSearchForm, MeetingUpdateForm

from app.setup import db

meeting = Blueprint('meeting', __name__)


@meeting.route('/', methods=['GET', 'POST'])
@login_required
def home():
    usr = current_user._get_current_object()
    create_form = MeetingCreateForm(request.form)
    if request.method == 'GET':
        res = []
        for meet in usr.meetings:
            res.append({'name': meet.name})
        return render_template('meeting.html', meetings=usr.meetings, form=create_form)

    # user requests a search
    if request.form['submit'] == 'search':
        search_form = MeetingSearchForm(request.form)
        if search_form.validate():
            criterium = search_form.criteria.data.split(" ")
            users = list(filter(lambda x: "@" in x, criterium))
            criterium = list(filter(lambda x: "@" not in x, criterium))
            meetings = usr.meetings

            # search by name
            for c in criterium:
                meetings = list(filter(lambda x: c.lower() in x.name.lower(), meetings))
            
            # search by users
            for u in users:
                uq = User.objects(email__iexact=u[1:])
                if len(uq) != 0:
                    meetings = list(filter(lambda x: uq[0] in x.members, meetings))

            return render_template('meeting.html', meetings=meetings, form=create_form)
    
    if request.form['submit'] == 'update':
        update_form = MeetingUpdateForm(request.form)
        if update_form.validate():
            query = Meeting.objects(id__exact=request.form.get('meeting_id'))
            if len(query) != 0:
                meeting = query[0]

                # update name
                meeting.name = request.form.get('name')
                flash('Successfully updated meeting!')

                del_user_emails = request.form.get('del_emails')                
                new_user_emails = request.form.get('add_emails')

                members = meeting.members

                # delete

                if len(del_user_emails) != 0:
                    del_list = del_user_emails.split(" ")
                    del_users = User.objects(email__in=del_list)

                    for u in del_users:
                        if meeting in u.meetings:
                            u.meetings.remove(meeting)
                            u.save() 
                
                    members = list(filter(lambda x: x not in del_users, members))
                
                if len(new_user_emails) != 0:
                    new_list = new_user_emails.split(" ")
                    new_users = User.objects(email__in=new_list)

                    for u in new_users:
                        if u not in members:
                            members.append(u)

                            if meeting not in u.meetings:
                                u.meetings.append(meeting)
                                u.save()
                
                meeting.members = members
                meeting.save()
                return redirect(url_for('meeting.home'))
            else:
                flash('Could not find Meeting')
                return redirect(url_for('meeting.home'))
        flash('Invalid Input')
        return redirect(url_for('meeting.home'))


    if create_form.validate():
        try:
            # generate list of users that will be in the meeting
            emails = create_form.emails.data.split(" ")
            emails.append(current_user.email)

            # grab the list of valid users
            query = User.objects(email__in=emails)
            query_emails = [u.email for u in query]

            # validate that all the members exist
            if len(emails) == len(query):
                # add the meeting to each user's meetings list
                m = Meeting(name=create_form.name.data,
                            members=query, owner=current_user._get_current_object(), active=True).save()
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
