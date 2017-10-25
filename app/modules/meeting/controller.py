import json
import requests
import string
import time
from datetime import datetime, timedelta

from app.modules.meeting.model import Meeting, MeetingCreateForm, \
    MeetingUpdateForm, MeetingDeleteForm
from app.modules.auth.model import User
from app.modules.tag.model import Tag

from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, jsonify
from flask_security import current_user, login_required


meeting = Blueprint('meeting', __name__)


def filter_form(form):
    """ Router for CRUD Forms that were Recieved on the Meeting Dashboard """

    if form['submit'] == 'create':
        return create_meeting(form)
    elif form['submit'] == 'update':
        return update_meeting(form)
    elif form['submit'] == 'delete':
        return delete_meeting(form)

    flash('error Could not Fulfill Request. Please Try Again.')
    return redirect(url_forl('meeting.home'))


@meeting.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """ Displays All of the Current Users Meetings on the Meeting Dashboard """
    if request.method == 'POST':
        return filter_form(request.form)

    user = current_user._get_current_object()
    return render_template('meeting/dashboard.html', meetings=user.meetings)


@meeting.route('/create', methods=['POST'])
@login_required
def create_meeting(form=None):
    """ Creates a new Meeting. """

    if form is not None:
        create_form = MeetingCreateForm(form)
        if create_form.validate():
            try:
                user = current_user._get_current_object()

                # generate the list of users that will be in the meeting
                emails = create_form.emails.data.split(" ")
                emails.append(user.email)

                # generate the list of valid emails
                query = User.objects(email__in=emails)
                valid_emails = [u.email for u in query]

                if len(emails) == len(emails):
                    # validate and create the meeting
                    m = Meeting(name=create_form.name.data,
                                members=query, owner=user, active=True).save()

                    # insert the meeting in each user's list of meetings
                    for u in query:
                        u.meetings.append(m)
                        u.save()

                    flash('success New Meeting has been Created with Member(s): {}'.format(", ".join(valid_emails)))
                    return redirect(request.args.get('next') or url_for('meeting.home'))
                else:
                    # determine the invalid emails
                    invalid_emails = list(set(emails) - set(valid_emails))
                    flash('error Could not Create Meeting. We Were Unable to Find User(s): {}'.format(
                        invalid_emails))
            except Exception as e:
                flash('error An Error has occurred, Please Try Again. {}'.format(e))
        else:
            # failed to validate form
            flash('error Could not Create New Meeting, Please Try Again.')
        return redirect(request.args.get('next') or url_for('meeting.home'))

    flash('error Invalid Request to Create New Meeting.')
    return redirect(url_for('meeting.home'))


@meeting.route('/update', methods=['PUT'])
@login_required
def update_meeting(form=None):
    """ Updates an Existing Meeting """

    if form is not None:
        update_form = MeetingUpdateForm(form)
        if update_form.validate():
            try:
                # extract the form data
                name = update_form.name.data
                emails_to_add_str = update_form.emails_to_add.data
                emails_to_remove_str = update_form.emails_to_remove.data

                # search for the meeting
                meeting = Meeting.objects.get(id=update_form.meeting_id.data)

                members = meeting.members

                # remove the undesired members
                if len(emails_to_remove_str) != 0:
                    emails_to_remove = emails_to_remove_str.split(" ")
                    members_to_remove = User.objects(
                        email__in=emails_to_remove)

                    # remove the meeting from each members list of meetings
                    for member in members_to_remove:
                        if meeting in member.meetings:
                            member.meetings.remove(meeting)
                            member.save()

                    # remove the members from the list
                    members = list(filter(
                        lambda x: x not in members_to_remove, members))

                # add the new members
                if len(emails_to_add_str) != 0:
                    emails_to_add = emails_to_add_str.split(" ")
                    members_to_add = User.objects(email__in=emails_to_add)

                    for member in members_to_add:
                        # add member to the meeting's list of members
                        if member not in members:
                            members.append(member)

                        # add meeting to the member's list of meetings
                        if meeting not in member.meetings:
                            member.meetings.append(meeting)
                            member.save()

                # save the changes
                meeting.name = name
                meeting.members = members
                meeting.save()

                flash('success Meeting has been Successfully Updated.')
                return redirect(request.args.get('next') or url_for('meeting.home'))
            except Exception as e:
                flash('error An Error has Occurred, Please Try Again. {}'.format(e))
                return redirect(request.args.get('next') or url_for('meeting.home'))
        else:
            # failed to validate form
            flash('error Could not Update Meeting, Please Try Again.')
            return redirect(request.args.get('next') or url_for('meeting.home'))
    flash('error Invalid Request to Update a Meeting.')
    return redirect(request.args.get('next') or url_for('meeting.home'))


@meeting.route('/delete', methods=['POST'])
@login_required
def delete_meeting(form=None):
    """ Deletes an Existing Group """

    if form is not None:
        delete_form = MeetingDeleteForm(form)
        if delete_form.validate():
            try:
                user = current_user._get_current_object()
                meeting = Meeting.objects.get(id=delete_form.meeting_id.data)

                members = meeting.members
                owner = meeting.owner

                # user is not the owner of the group and cannot delete
                if user != owner:
                    flash('error You do not have Permission to Delete this Meeting.')
                    return redirect(request.args.get('next') or url_for('meeting.home'))

                # remove the meeting from each member's list of meetings
                for member in members:
                    if meeting in member.meetings:
                        member.meetings.remove(meeting)
                        member.save()

                # TODO: handle tags

                # remove meeting from owner's list of meetings
                if meeting in owner.meetings:
                    owner.meetings.remove(meeting)
                    owner.save()

                meeting.delete()

                flash('success Meeting Successfully Deleted.')
                return redirect(request.args.get('next') or url_for('meeting.home'))
            except Exception as e:
                flash('error An Error has Occured, Please Try Again.'
                      '{}'.format(str(e)))
        else:
            # failed to validate form
            flash('error Could not Delete Meeting, Please Try Again.')
    return redirect(request.args.get('next') or url_for('meeting.home'))


@meeting.route('/search=<string:query>', methods=['GET', 'POST'])
@login_required
def search_meetings(query):
    """ Displays the Meetings to the User's Dashboard that match the given criteria """

    if request.method == 'POST':
        return filter_form(request.form)

    meetings = current_user._get_current_object().meetings
    search = query.split(" ")

    # search is too expensive
    if len(search) > 20:
        flash('error Could not fulfill search request.')
        return redirect(request.args.get('next') or url_for('meeting.home'))

    # get the list of users to search for
    users = list(filter(lambda x: "@" in x, search))

    # get the list of tags to search for
    tags = list(filter(lambda x: "#" in x, search))

    # get the other search criteria
    search = list(set(search) - set(users) - set(tags))

    # filter the meetings to only contain meetings with desired tags
    for t in tags:
        try:
            tag = Tag.objects.get(string=t[1:])
            meetings = list(filter(lambda x: tag in x.tags, meetings))
        except Exception as e:
            return render_template('meeting.home', meetings=[])

    # filter the meetings to only contain meetings with desired members
    for u in users:
        try:
            user = User.objects.get(email=u[1:])
            meetings = list(filter(
                lambda x: user in x.members, meetings))
        except Exception as e:
            return render_template('meeting.home', meetings=[])

    # filter the meetings to only contain meetings with the desired text
    for c in search:
        meetings = list(filter(
            lambda x: c.lower() in x.name.lower(), meetings))

    # reset the page and only show the desired meetings
    return render_template('meeting/dashboard.html', meetings=meetings)


@meeting.route('/info/<string:meeting_id>', methods=['GET'])
@login_required
def get_active_meeting(meeting_id):
    if len(meeting_id) == 24 and all(c in string.hexdigits for c in meeting_id):
        try:
            meeting = Meeting.objects.get(id=meeting_id)

            if current_user not in meeting.members:
                flash('error You are not a member of that meeting.')
                return redirect(url_for('meeting.meetings_page'))
            return jsonify(meeting)
        except Exception as e:
            flash('error An Error Occured. {}'.format(str(e)))
            return redirect(request.args.get('next') or url_for('meeting.home'))
    flash('error Invalid Meeting Id.')
    return redirect(request.args.get('next') or url_for('meeting.meetings_page'))
