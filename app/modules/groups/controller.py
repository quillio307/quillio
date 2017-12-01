import string

from app.modules.auth.model import User
from app.modules.groups.model import Group, GroupCreateForm, GroupUpdateForm, \
    GroupDeleteForm
from app.modules.meetings.model import Meeting, MeetingCreateForm, MeetingUpdateForm, MeetingDeleteForm
from flask import Blueprint, request, render_template, flash, redirect, \
    url_for, jsonify
from flask_security import login_required, current_user


groups = Blueprint('groups', __name__)


def filter_form(form):
    """ Router for CRUD Forms that were Recieved on the Group Dashboard """

    if form['submit'] == 'create':
        return create_group(form)
    elif form['submit'] == 'update':
        return update_group(form)
    elif form['submit'] == 'delete':
        return delete_group(form)

    flash('error Could not Fulfill Request. Please Try Again.')
    return redirect(url_for('meetings.home'))


def group_filter_form(form):
    """ Router for CRUD Forms Recevied in the Group Landing Page """

    if form['submit'] == 'create':
        return create_group_meeting(form)
    elif form['submit'] == 'update':
        return update_group_meeting(form)
    elif form['submit'] == 'delete':
        return delete_group_meeting(form)

    flash('error Could not fullfill request. Please try again')
    return redirect(url_form('groups.home'))


@groups.route('/delete-meeting', methods=['POST'])
@login_required
def delete_group_meeting(form=None):
    """ Delete and existing group meeting """

    if form is None:
        flash('error Invalid Request to delete meeting.')
        return redirect(request.args.get('next') or url_for('groups.home'))

    delete_form = MeetingDeleteForm(form)

    if not delete_form.validate():
        flash('error You do not have permission to delete this meeting.')
        return redirect(url_form('groups.home'))

    try:
        user = current_user._get_current_object()
        meeting = Meeting.objects.get(id=delete_form.meeting_id.data)
        groups = Group.objects(meetings__contains=meeting)

        members = meeting.members
        owner = meeting.owner

        # user is not the owner of group and cannot delete
        if user != owner:
            flash('error You do not have permission to delete this meeting.')
            return redirect(url_for('groups.home'))

        # remove the meeting from each member's list of meeting
        for member in members:
            if meeting in member.meetings:
                member.meetings.remove(meeting)
                member.meeting_count = member.meeting_count - 1
                member.save()

        # remove meeting from owner's list of meetings
        if meeting in owner.meetings:
            owner.meetings.remove(meeting)
            owner.meeting_count = member.meeting_count - 1
            owner.save()

        # remove meeting from owner's list of groups
        for group in user.groups:
            if meeting in group.meetings:
                group.meetings.remove(meeting)
                group.save()
        meeting.delete()
        flash('success Meeting successfully deleted')

    except Exception as e:
        flash('error An error has occured, please try again {}'.format(str(e)))
    return redirect(request.args.get('next') or url_for('groups.home'))


@groups.route('/update-meeting', methods=['POST'])
@login_required
def update_group_meeting(form=None):
    """ Update and existing meeting from the group landing page"""
    if form is None:
        flash("error Invalid Request to update meeting")
        return redirect(request.args.get('next') or url_for('groups.home'))
    update_form = MeetingUpdateForm(form)

    if not update_form.validate():
        flash("error Could not update meeting, please try again")
        return redirect(request.args.get('next') or url_for('groups.home'))
    try:
        # extract form data
        name = update_form.name.data
        emails_to_add_str = update_form.emails_to_add.data
        emails_to_remove_str = update_form.emails_to_remove.data

        # search for the meeting
        meeting = Meeting.objects.get(id=update_form.meeting_id.data)

        members = meeting.members

        # remove the undesired members
        if len(emails_to_remove_str) != 0:
            emails_to_remove = emails_to_remove_str.split("")
            members_to_remove = User.objects(email__in=emails_to_remove)

            # remove the meeting from each members list of meetings
            for member in members_to_remove:
                if meeting in member.meetings:
                    member.meeting_count = member.meeting_count - 1
                    member.meetings.remove(meeting)
                    member.save()
            # remove members from the list
            members = list(filter(
                lambda x: x not in members_to_remove, members))

        # add new members
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

        # save all the changes
        meeting.name = name
        meeting.members = members
        meeting.save()

        flash('success Meeting has been successfully updated.')
    except Exception as e:
        flash("error An error has occcured, please try again: {}".format(e))

    return redirect(url_for('groups.home'))


@groups.route('/create-meeting', methods=['POST'])
@login_required
def create_group_meeting(form=None):
    """ Creates a new meeting from the group landing page """
    if form is None:
        flash("error Invalid Request to create meeting")
        return redirect(request.args.get('next') or url_for('groups.home'))
    create_form = MeetingCreateForm(form)

    if not create_form.validate():
        flash("error Could not create new meeting, please try again")
        return redirect(request.args.get('next') or url_for('groups.home'))
    try:
        user = current_user._get_current_object()

        emails = create_form.emails.data.split(" ")
        emails.append(user.email)

        # generate list of valid emails - should be valid unless a user is deleted
        query = User.objects(email__in=emails)
        valid_emails = [u.email for u in query]

        # check if emails are complete, if not, display incorrect and cancel request
        if len(valid_emails) != len(emails):
            invalid_emails = list(set(emails) - set(valid_emails))
            flash("error We were unable to find user(s): {}".format(invalid_emails))
            return redirect(url_for('groups.home'))
        # validate and create meeting
        m = Meeting(name=create_form.name.data,
                    members=query,
                    owner=user,
                    meeting_nature=create_form.nature.data,
                    active=False).save()
        # insert meeting into each user's list of meetings
        for u in query:
            u.meetings.append(m)
            u.meeting_count = u.meeting_count + 1
            u.save()

        # insert meeting into this group
        # query to find group associated
        g = Group.objects.get(members=query)
        g.meetings.append(m)
        g.save()

        flash("success Meeting successfully created with group {}".format(g.name))
        return redirect(url_for('groups.get_group_by_id', group_id=g.id))
    except Exception as e:
        flash("error An error has occcured, please try again: {}".format(e))
    return redirect(url_for('groups.home'))


@groups.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """ Displays All of the Current User's Groups on the Group Dashboard """
    if request.method == 'POST':
        return filter_form(request.form)

    user = current_user._get_current_object()
    return render_template('group/dashboard.html', groups=user.groups)


@groups.route('/create', methods=['POST'])
@login_required
def create_group(form=None):
    """ Creates a new Group. """

    if form is None:
        flash('error Invalid Request to Create New Group.')
        return redirect(url_for('groups.home'))

    create_form = GroupCreateForm(form)

    if not create_form.validate():
        flash('error Could not Create New Group, Please Try Again.')
        return redirect(request.args.get('next') or url_for('groups.home'))

    try:
        user = current_user._get_current_object()

        # generate the list of requested member emails
        emails = create_form.emails.data.split(" ")
        emails.append(user.email)

        # generate the list of valid emails
        query = User.objects(email__in=emails)
        valid_emails = [u.email for u in query]

        # validate and create the new group
        if len(emails) == len(valid_emails):

            g = Group(name=create_form.name.data, members=query,
                      admins=[user]).save()

            # add the group to each member's list of groups
            for u in query():
                u.groups.append(g)
                u.save()

            flash('success New Group Created with Member(s): {}'.format(
                ", ".join(valid_emails)))
            return redirect(request.args.get('next') or url_for('groups.home'))
        else:
            # determine the invalid emails
            invalid_emails = list(set(emails) - set(valid_emails))
            flash('error Could not Create New Group. Unable to Find User(s):'
                  '{}'.format(invalid_emails))
    except Exception as e:
        flash('error An Error has Occured, Please Try Again. '
              '{}'.format(str(e)))

    return redirect(request.args.get('next') or url_for('groups.home'))


@groups.route('/update', methods=['POST'])
@login_required
def update_group(form=None):
    """ Updates an Existing Group """

    if form is None:
        flash('error Invalid Request to Update Group.')
        return redirect(url_for('groups.home'))

    update_form = GroupUpdateForm(form)

    if not update_form.validate():
        flash('error Could Not Update Group, Please Try Again.')
        return redirect(request.args.get('next') or url_for('groups.home'))

    try:
        # extract the form data
        name = update_form.name.data
        description = update_form.description.data
        emails_to_add_str = update_form.emails_to_add.data
        admin_emails_to_add_str = update_form.admin_emails_to_add.data
        emails_to_remove_str = update_form.emails_to_remove.data

        group = Group.objects.get(id=update_form.group_id.data)

        members = group.members
        admins = group.admins

        # remove the undesired members
        if len(emails_to_remove_str) != 0:
            emails_to_remove = emails_to_remove_str.split(" ")
            members_to_remove = User.objects(
                email__in=emails_to_remove)

            # remove the group from each members list of groups
            for member in members_to_remove:
                if group in member.groups:
                    member.groups.remove(group)
                    member.save()

            # remove the members from the list
            members = list(filter(
                lambda x: x not in members_to_remove, members))

        # add the new members
        if len(emails_to_add_str) != 0:
            emails_to_add = emails_to_add_str.split(" ")
            members_to_add = User.object(email__in=emails_to_add)

            for member in members_to_add:
                # add member to the group's list of members
                if member not in members:
                    members.append(member)

                # add group to the member's list of groups
                if group not in member.groups:
                    member.groups.append(group)
                    member.save()

        # add the new admins
        if len(admin_emails_to_add_str) != 0:
            admin_emails_to_add = admin_emails_to_add_str.split(" ")
            admins_to_add = User.objects(
                email__in=admin_emails_to_add)

            for admin in admins_to_add:
                # add admin to the group's list of admins
                if admin not in admins:
                    admins.append(admin)

                # add admin to the group's list of members
                if admin not in members:
                    members.append(admin)

                # add group to the admin's list of groups
                if group not in admin.groups:
                    admin.groups.append(group)
                    admin.save()

        # update the description
        if len(description) != 0:
            group.description = description

        # save the changes
        group.name = name
        group.members = members
        group.admins = admins
        group.save()

        flash('success Group Successfully Updated')

    except Exception as e:
        flash('error Unable to Update Group at this Time, Please Try Again.'
              '{}'.format(str(e)))
        print(str(e))

    return redirect(request.args.get('next') or url_for('groups.home'))


@groups.route('/delete', methods=['POST'])
@login_required
def delete_group(form=None):
    """ Deletes an Existing Group """

    if form is None:
        flash('error Invalid Request to Delete Group.')
        return redirect(request.args.get('next') or url_for('groups.home'))

    delete_form = GroupDeleteForm(form)

    if not delete_form.validate():
        flash('error Could not Delete Group, Please Try Again.')
        return redirect(request.args.get('next') or url_for('groups.home'))

    try:
        user = current_user._get_current_object()
        group = Group.objects.get(id=delete_form.group_id.data)

        members = group.members
        admins = group.admins
        meetings = group.meetings
        # validate that the user is an admin for the group
        if user not in admins:
            flash('error You do not have permission to delete this group.')
            return redirect(request.args.get('next') or
                            url_for('groups.home'))

        # remove the group from each member's list of groups
        for member in members:
            if group in member.groups:
                member.groups.remove(group)
                member.save()

        # remove the group from each admin's list of groups
        for admin in admins:
            if group in admin.groups:
                admin.groups.remove(group)
                admin.save()

        # delete all meetings associated with group
        for meeting in meetings:
            # remove meeting from all member's list of meetings
            for member in members:
                member.meetings.remove(meeting)
                member.save()

            # remove meeting from each admin's list of meetings
            for admin in admins:
                admin.meetings.remove(meeting)
                admin.save()

            # now delete the entire meeting from the database
            meeting.delete()
        group.delete()

        flash('success Group Successfully Deleted')
    except Exception as e:
        flash('error An Error has Occured, Please Try Again.'
              '{}'.format(str(e)))

    return redirect(request.args.get('next') or url_for('groups.home'))


@groups.route('/search=<string:query>', methods=['GET', 'POST'])
@login_required
def search_groups(query):
    """ Displays the Groups that match the query on the Group Dashboard """

    if request.method == 'POST':
        return filter_form(request.form)

    groups = current_user._get_current_object().groups
    search = query.split(" ")

    # search is too expensive
    if len(search) > 20:
        flash('error Could not Fulfill Search Request.')
        return redirect(request.args.get('next') or url_for('groups.home'))

    # get the list of users to search for
    users = list(filter(lambda x: "@" in x, search))

    # get the other search criteria
    search = list(filter(lambda x: "@" not in x, search))

    # filter the groups by user
    for u in users:
        try:
            user = User.objects.get(email=u[1:])
            groups = list(filter(lambda x: user in x.members, groups))
        except Exception as e:
            return render_template('group/dashboard.html', groups=[])

    # filter the meetings by name
    for c in search:
        groups = list(filter(lambda x: c.lower() in x.name.lower(), groups))

    # reset the page and only show the matched groups
    return render_template('group/dashboard.html', groups=groups)


@groups.route('/<group_id>', methods=['GET', 'POST'])
@login_required
def get_group_by_id(group_id, form=None):
    if request.method == 'POST':
        return group_filter_form(request.form)

    # validate the given id
    if len(group_id) != 24 or not all(c in string.hexdigits for c in group_id):
        flash('error Invalid Group ID')
        return redirect(request.args.get('next') or url_for('groups.home'))

    try:
        user = current_user._get_current_object()
        group = Group.objects.get(id=group_id)
        if user not in group.members:
            flash('error You Are Not A Member Of This Group.')
            return redirect(request.args.get('next') or url_for('groups.home'))

        emails = []
        for u in group.members:
            if u.email != user.email:
                emails.append(u.email)
        emails = " ".join(emails)
        form = MeetingCreateForm()
        return render_template('group/group.html', group=group, stats=group_stats(group_id), emails=emails, form=form)

    except Exception as e:
        flash('error An Error Occured. {}'.format(str(e)))
        return redirect(request.args.get('next') or url_for('groups.home'))


@login_required
def group_stats(group_id):
    if len(group_id) != 24 or not all(c in string.hexdigits for c in group_id):
        flash('error Invalid Group ID')
        return redirect(request.args.get('next') or url_for('groups.home'))

    response = dict()

    try:
        user = current_user._get_current_object()
        groups = current_user._get_current_object().groups
        group = Group.objects.get(id=group_id)

        if user not in group.members:
            return {'status': 'invalid permission'}

        contributions = group.get_member_contributions()
        sorted_contributors = sorted(contributions, key=contributions.get, reverse=True)
        sorted_contributors = sorted_contributors[:3]
        del(sorted_contributors[3:])

        tags = group.get_frequent_tags()
        sorted_tags = sorted(tags, key=tags.get, reverse=True)
        del(sorted_tags[3:])

        topics = group.get_frequent_topics()
        sorted_topics = sorted(topics, key=topics.get, reverse=True)
        del(sorted_topics[3:])

        # response['contribution'] = group.update_contr()
        response['contributors'] = sorted_contributors
        response['tags'] = sorted_tags
        response['topics'] = sorted_topics

        return response
    except Exception as e:
        response['error'] = str(e)

    response['status'] = 'failure'
    return response
