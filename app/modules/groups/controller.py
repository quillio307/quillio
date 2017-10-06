import json
import string

from flask import Blueprint, abort, request, render_template, flash, redirect, \
    url_for, jsonify
from flask_security import Security, login_required

from app.modules.auth.model import User
from app.modules.groups.model import Group, GroupCreateForm, GroupSearchForm, \
    GroupUpdateForm
from flask_login import current_user
from app.setup import login_manager, db

groups = Blueprint('groups', __name__)


@groups.route('/', methods=['GET', 'POST'])
@login_required
def home():
    usr = current_user._get_current_object()
    create_form = GroupCreateForm(request.form)
    if request.method == 'GET':
        res = []
        for group in usr.groups:
            res.append({'name': group.name, 'admin': group.user_is_admin(usr)})
        return render_template('groups.html', groups=usr.groups, form=create_form)

    # user requests a search
    if request.form['submit'] == 'search':
        search_form = GroupSearchForm(request.form)
        if search_form.validate():
            criterium = search_form.criteria.data.split(" ")
            users = list(filter(lambda x: "@" in x, criterium))
            criterium = list(filter(lambda x: "@" not in x, criterium))
            groups = usr.groups

            # search by name 
            for c in criterium:
                groups = list(filter(lambda x: c.lower() in x.name.lower(), groups))

            # search by user
            for u in users:
                flash('seing if {} is in any groups'.format(u[1:]))
                uq = User.objects(email__iexact=u[1:])
                if len(uq) != 0:
                    groups = list(filter(lambda x: uq[0] in x.members, groups))

            return render_template('groups.html', groups=groups, form=create_form)

    # user requests an update
    if request.form['submit'] == 'update':
        update_form = GroupUpdateForm(request.form)
        if update_form.validate():
            query = Group.objects(id__exact=request.form.get('group_id'))
            if len(query) != 0:
                group = query[0]

                # update name and description
                group.name = request.form.get('name')
                group.description = request.form.get('description')

                del_user_emails = request.form.get('del_emails')
                new_user_emails = request.form.get('add_emails')
                new_admin_emails = request.form.get('add_admin_emails')

                # delete the users
                members = group.members

                if len(del_user_emails) != 0:
                    del_list = del_user_emails.split(" ")
                    del_users = User.objects(email__in=del_list)
                    # remove group from user
                    for u in del_users:
                        if group in u.groups:
                            flash('removed {0} from {1}'.format(group.name, u.name))
                            u.groups.remove(group)
                            u.save()

                    members = list(filter(lambda x: x not in del_users, members))
                
                # add the users
                if len(new_user_emails) != 0:
                    new_list = new_user_emails.split(" ")
                    new_users = User.objects(email__in=new_list)
                    for u in new_users:
                        if u not in members:
                            members.append(u)
                            # add group to user
                            if group not in u.groups:
                                u.groups.append(group)
                                u.save()
                
                admins = group.admins

                # add the admins
                if len(new_admin_emails) != 0:
                    new_admin_list = new_admin_emails.split(" ")
                    new_admins = User.objects(email__in=new_admin_list)

                    for a in new_admins:
                        if a not in admins:
                            admins.append(a)
                        if a not in members:
                            members.append(a)
                        if group not in a.groups:
                            a.groups.append(group)

                group.members = members
                group.admins = admins
                group.save()
                flash('successfully updated group!')
                return redirect(url_for('groups.home'))
            flash('could not find the group')
            return redirect(url_for('groups.home')) 
        else:
            flash('Invalid Input, Please try again!')
            return redirect(url_for('groups.home'))

    # user requests a new group
    if create_form.validate():
        try:
            emails = create_form.emails.data.split(" ")
            emails.append(current_user.email)

            query = User.objects(email__in=emails)
            query_emails = [u.email for u in query]

            if len(emails) == len(query):
                g = Group(name=create_form.name.data,
                          members=query, admins=[current_user._get_current_object()]).save()

                for u in query:
                    u.groups.append(g)
                    u.save()
                flash('New Group created with member(s): {}'
                      .format(query_emails))
                return redirect(url_for('groups.home'))
            else:
                invalid = list(set(emails) - set(query_emails))
                flash('Could not find user(s): {}'.format(invalid))
                return redirect(url_for('groups.home'))
        except Exception as e:
            flash('A problem has occurred, please try again! {}'.format(e))
            return redirect(url_for('groups.home'))

    flash('Invalid input.  Please try again!')
    return redirect(url_for('groups.home'))


@groups.route('/is/admin/<string:group_id>')
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


@groups.route('/get/<string:group_id>')
@login_required
def get_group_by_id(group_id):
    if len(group_id) == 24 and all(c in string.hexdigits for c in group_id):
        query = Group.objects(id__exact=group_id)
        if len(query) > 0:
            if current_user not in query[0].members:
                flash('You are not a member of that group.')
                return redirect(url_for('groups.home'))
            return jsonify({'Group': query})
        else:
            flash('Group not found')
            return redirect(url_for('groups.home'))
    flash('Invalid Group Id.')
    return redirect(url_for('groups.home'))


# AMMO CODE

# @groups.route('/all', methods=['GET'])
# @login_required
# def all_groups():
#     usr = current_user._get_current_object()
#     res = []
#     for group in usr.groups:
#         res.append({'name': group.name, 'admin': group.user_is_admin(usr)})
#     return json.dumps(res)


#@groups.route('/create', methods=['POST'])
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
