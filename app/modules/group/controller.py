import string

from app.modules.auth.model import User
from app.modules.group.model import Group, GroupCreateForm, GroupUpdateForm

from flask import Blueprint, request, render_template, flash, redirect, \
    url_for, jsonify
from flask_security import Security, login_required, current_user


group = Blueprint('group', __name__)


def filter_form(form):
    """ Router for CRUD Forms that were Recieved on the Group Dashboard """

    if form['submit'] == 'create':
        return create_group(form)
    elif form['submit'] == 'update':
        return update_group(form)

    flash('Could not Fulfill Request. Please Try Again.')
    return redirect(url_for('meeting.home'))


@group.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """ Displays All of the Current User's Groups on the Group Dashboard """
    if request.method == 'POST':
        return filter_form(request.form)

    user = current_user._get_current_object()
    return render_template('group/dashboard.html', groups=user.groups)


@group.route('/create', methods=['POST'])
@login_required
def create_group(form=None):
    """ Creates a new Group. """

    if form is not None:
        create_form = GroupCreateForm(form)
        if create_form.validate():
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
                    g = Group(name=create_form.name.data, members=query, admins=[user]).save()

                    # add the group to each member's list of groups
                    for u in query():
                        u.groups.append(g)
                        u.save()

                    flash('New Group Created with Member(s): {}'.format(str(valid_emails)))
                    return redirect(request.args.get('next') or url_for('group.home'))
                else:
                    # determine the invalid emails
                    invalid_emails = list(set(emails) - set(valid_emails))
                    flash('Could not Create New Group. Unable to Find User(s): {}'.format(invalid_emails))
            except Exception as e:
                flash('An Error has Occured, Please Try Again. {}'.format(str(e)))
        else:
            # failed to validate form
            flash('Could not Create New Group, Please Try Again.')
        return redirect(request.args.get('next') or url_for('group.home'))

    flash('Invalid Request to Create New Group.')
    return redirect(url_for('group.home'))


@group.route('/update', methods=['POST'])
@login_required
def update_group(form=None):
    """ Updates an Existing Group """

    if form is not None:
        update_form = GroupUpdateForm(form)
        if update_form.validate():
            try:
                # extract the form data
                name = update_form.name.data
                description = update_form.description.data
                emails_to_add_str = update_form.emails_to_add.data
                admin_emails_to_add_str = update_form.admin_emails_to_add.data
                emails_to_remove_str = update_form.emails_to_remove.data

                # search for the group
                query = Group.objects(id__exact=update_form.group_id.data)

                if len(query) > 0:
                    group = query[0]
                    members = group.members
                    admins = group.admins

                    # remove the undesired members
                    if len(emails_to_remove_str) != 0:
                        emails_to_remove = emails_to_remove_str.split(" ")
                        members_to_remove = User.objects(email__in=emails_to_remove)

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
                        admins_to_add = User.objects(email__in=admin_emails_to_add)

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

                    flash('Group has been Successfully Updated')
                    return redirect(request.args.get('next') or url_for('group.home'))
                else:
                    flash('Unable to Update Group at this Time.')
            except Exception as e:
                flash('Unable to Update Group at this Time.  Please Try Again. {}'.format(str(e)))
        else:
            # failed to validate form
            flash('Could not Update Group, Please Try Again.')
        return redirect(request.args.get('next') or url_for('group.home'))

    flash('Invalid Request to Update Group.')
    return redirect(url_for('group.home'))


@group.route('/search=<string:query>', methods=['GET', 'POST'])
@login_required
def search_groups(query):
    """ Displays the Groups that Match the Given Query on the User's Group Dashboard """
    
    if request.method == 'POST':
        return filter_form(request.form)

    groups = current_user._get_current_object().groups
    search = query.split(" ")

    # get the list of users to search for
    users = list(filter(lambda x: "@" in x, search))

    # get the other search criteria
    search = list(filter(lambda x: "@" not in x, search))

    # search is too expensive
    if len(search) > 20:
        flash('Could not Fulfill Search Request.')
        return redirect(request.args.get('next') or url_for('group.home'))

    # filter the groups by user
    for u in users:
        user_query = User.objects(email__iexact=u[1:])
        if len(user_query) != 0:
            groups = list(filter(
                lambda x: user_query[0] in x.members, groups))
    
    # filter the meetings by name
    for c in search:
        groups = list(filter(
            lambda x: c.lower() in x.name.lower(), groups))
    
    # reset the page and only show the matched groups
    return render_template('group/dashboard.html', groups=groups)




@group.route('/is/admin/<string:group_id>')
@login_required
def get_group_admins(group_id):
    if len(group_id) == 24 and all(c in string.hexdigits for c in group_id):
        query = Group.objects(id__exact=group_id)
        if len(query) > 0:
            if current_user in query[0].admins:
                return jsonify({'is_admin': True, 'status': 200})
            return jsonify({'is_admin': False, 'status': 200})
        else:
            return jsonify({'status': 404})
    return jsonify({'status': 400}) 


@group.route('/info/<string:group_id>')
@login_required
def get_group_by_id(group_id):
    # validate the id given
    if len(group_id) == 24 and all(c in string.hexdigits for c in group_id):
        query = Group.objects(id__exact=group_id)
        if len(query) > 0:
            
            # check that the current user is in the group
            if current_user not in query[0].members:
                flash('You are not a member of that group.')
                return redirect(request.args.get('next') or url_for('group.home'))
            return jsonify(query)
        else:
            return redirect(request.args.get('next') or url_for('group.home'))
    flash('Invalid Group ID')
    return redirect(request.args.get('next') or url_for('group.home'))


# AMMO CODE

# @group.route('/all', methods=['GET'])
# @login_required
# def all_groups():
#     usr = current_user._get_current_object()
#     res = []
#     for group in usr.groups:
#         res.append({'name': group.name, 'admin': group.user_is_admin(usr)})
#     return json.dumps(res)


#@group.route('/create', methods=['POST'])
#@login_required
# def create_group():
#    usr = current_user._get_current_object()
#    req = request.get_json(silent=True)
#
#    if not('name' in req and 'members' in req and 'admins' in req):
#        abort(400)
#
#    members = []
#
#    for email in req['members']:
#        query = User.objects(email=email)
#        if len(query) == 0:
#            req['members'].remove(email)
#        else:
#            members.append(query[0])
#
#    if usr.email not in req['members']:
#        members.append(usr)
#
#    if len(members) <= 1:
#        abort(400)
#
#    admins = []
#
#    for admin_email in req['admins']:
#        for mem in members:
#            if mem.email == admin_email:
#                admins.append(mem)
#
#    if usr.email not in req['admins']:
#        admins.append(usr)
#
#    grp = Group(name=req['name'], members=members, admins=admins)
#    grp.save()
#
#    for member in members:
#        member.groups.append(grp)
#        member.save()
#
#    res = {'message': "Success"}
#    return json.dumps(res)
