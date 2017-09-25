from flask import Blueprint
from flask import request, render_template, jsonify, flash, redirect, url_for
from flask_login import LoginManager

from app.modules.auth.model import User, SignupForm

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
    form = SignupForm(request.form)
    if request.method == 'GET':
        return render_template('auth/signup.html', form=form)
    if form.validate():
        try:
            User(name=form.name.data, username=form.username.data, email=form.email.data, password=form.password.data).save()
            return redirect(url_for('auth_login'))
        except:
            return 'failure'
        return 'success'
    return 'invalid form'
