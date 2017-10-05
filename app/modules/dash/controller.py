from flask import Blueprint, render_template
from flask_security import login_required, roles_accepted, roles_required

dash = Blueprint('dash', __name__)


@dash.route('/home', methods=['GET'])
@login_required
def home():
    return render_template('dash/home.html')