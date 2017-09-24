from flask import Blueprint


auth = Blueprint('auth', __name__)


@auth.route('/login')
def auth_login():
    pass


@auth.route('/register')
def auth_register():
    pass


@auth.route('/register/user')
def auth_register_user():
    pass
