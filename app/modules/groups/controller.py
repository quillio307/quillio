from flask import Blueprint, abort, request
from flask_security import Security, login_required
from app.modules.auth.model import User
from app.modules.groups.model import Group
from flask_login import current_user
import json
from app.setup import login_manager, db

groups = Blueprint('groups', __name__)


@groups.route('/create', methods=['POST'])
@login_required
def create_group():
    usr = current_user._get_current_object()
    req = request.get_json(silent=True)

    if not('name' in req and 'members' in req and 'admins' in req):
        abort(400)

    members = []

    for email in req['members']:
        query = User.objects(email=email)
        if len(query) == 0:
            req.members.remove(email)
        else:
            members.append(query[0])

    if usr.email not in req['members']:
        members.append(usr)

    admins = []

    for admin_email in req['admins']:
        for mem in members:
            if mem.email == admin_email:
                admins.append(mem)

    if usr.email not in req['admins']:
        admins.append(usr)

    grp = Group(name=req['name'], members=members, admins=admins)
    grp.save()
    res = {'message': "Success"}
    return json.dumps(res)
