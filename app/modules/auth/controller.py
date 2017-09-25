from flask import Blueprint
from flask import request, render_template, jsonify
from flask_login import LoginManager

from app.modules.auth.model import User

auth = Blueprint('auth', __name__)

login_manager = LoginManager()


@auth.record_once
def on_load(state):
    login_manager.init_app(state.app)


@login_manager.user_loader
def user_loader(user_id):
    """ Reloads the user object from the user ID stored in the session. """
    query = User.objecst(id__exact=user_id)
    if len(query) == 0:
        return None
    return query[0]


@auth.route('/login', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    email = request.form['email']
    password = request.form['password']
    return jsonify({'email': email, 'password': password})


@auth.route('/signup', methods=['GET', 'POST'])
def auth_register():
    if request.method == 'GET':
        return render_template('auth/signup.html')
    name = request.form['name']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    User(name=name, email=email, username=username, password=password).save()
    return jsonify({'info': dir(app)})
    #return jsonify({
        #'name': name,
        #'email': email,
        #'username': username,
        #'password': password
        #})
