import json
import string

from flask import Blueprint, abort, request, render_template, flash, redirect, \
    url_for, jsonify
from flask_security import Security, login_required

from app.modules.auth.model import User
from app.modules.groups.model import Group, GroupForm
from flask_login import current_user
from app.setup import login_manager, db

groups = Blueprint('groups', __name__)


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


@groups.route('/all', methods=['GET'])
@login_required
def all_groups():
    usr = current_user._get_current_object()
    res = []
    for group in usr.groups:
        res.append({'name': group.name, 'admin': group.user_is_admin(usr)})
    return json.dumps(res)


@groups.route('/', methods=['GET', 'POST'])
@login_required
def home():
    form = GroupForm(request.form)
    if request.method == 'GET':
        usr = current_user._get_current_object()
        res = []
        for group in usr.groups:
            res.append({'name': group.name, 'admin': group.user_is_admin(usr)})
        return render_template('groups.html', groups=res, form=form)

    if form.validate():
        try:
            emails = form.emails.data.split(" ")
            emails.append(current_user.email)

            query = User.objects(email__in=emails)
            query_emails = [u.email for u in query]

            if len(emails) == len(query):
                g = Group(name=form.name.data,
                          members=query, admins=[]).save()

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
