from flask import Blueprint
from flask_security import Security, login_required
from app.modules.groups.model import Group
from flask_login import current_user
from flask import request
import json
from app.setup import login_manager, db

groups = Blueprint('groups', __name__)


@groups.route('/create', methods=['POST'])
@login_required
def create_group():
    req = request.get_json(silent=True)
    grp = Group(name=req['name'], members=[current_user._get_current_object()], admins=[current_user._get_current_object()])
    grp.save()
    res = {'user': current_user.email, 'req': req}
    return json.dumps(res)

'''
@groups.route('/', methods=['POST'])
def createGroup():
    return ""'''