from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_security import login_user, logout_user, login_required
from passlib.hash import bcrypt

from app.modules.auth.model import SignupForm, LoginForm
from app.modules.auth.model import User
from app.modules.auth.model import user_datastore
from app.modules.meeting.controller import meeting
from app.setup import login_manager


auth = Blueprint('auth', __name__)

@login_manager.user_loader
def user_loader(user_id):
    """ Reloads the user object from the user ID stored in the session. """
    user = user_datastore.find_user(id=user_id)
    if user is not None:
        return user
    return None


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    if request.method == 'GET':
        return render_template('auth/signup.html', form=form)
    if form.validate():
        try:
            # add user to the database
            pwd_hash = bcrypt.encrypt(form.password.data)
            user = user_datastore.create_user(
                email=form.email.data,
                name=form.name.data,
                password=pwd_hash)

            # set the user to have unregistered and default permissions
            unreg = user_datastore.find_or_create_role('unregistered')
            default = user_datastore.find_or_create_role('default')
            user_datastore.add_role_to_user(user, unreg)
            user_datastore.add_role_to_user(user, default)

            login_user(user)
            return redirect(request.args.get('next') or url_for('meeting.meetings_page'))
        except Exception as e:
            flash('A Problem has Occured, Please Try Again! {}'.format(e))
            return redirect(url_for('auth.signup'))
    flash('Invalid Email or Password')
    return redirect(url_for('auth.signup'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'GET':
        return render_template('auth/login.html', form=form)
    if form.validate():
        user = user_datastore.find_user(email=form.email.data)
        if user is not None:
            if bcrypt.verify(form.password.data, user.password):
                login_user(user)
                flash('Logged in successfully, {}'.format(user.name))
                return redirect(request.args.get('next') or url_for('meeting.meetings_page'))
    flash('Invalid Email or Password')
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
