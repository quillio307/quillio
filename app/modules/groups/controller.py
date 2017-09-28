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
def createGroup():
    content = request.get_json(silent=True)
    res = {'user': current_user.email, 'req': content}
    return json.dumps(res)
'''
@groups.route('/', methods=['POST'])
def createGroup():
    return ""'''