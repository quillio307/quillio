from flask import Blueprint, request, render_template
# from app.modules.auth import User


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'GET':
        return render_template('auth/login.html')


@auth.route('/register')
def auth_register():
    pass


@auth.route('/register/user')
def auth_register_user():
    pass
