from app.modules.auth.model import User, SignupForm, LoginForm, \
    user_datastore
from app.modules.meeting.controller import meeting

from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_security import login_user, logout_user, login_required
from flask_security.utils import hash_password, verify_password


auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    if request.method == 'GET':
        return render_template('auth/signup.html', form=form)
    if form.validate():
        try:
            # add user to the database
            user = user_datastore.create_user(
                email=form.email.data,
                name=form.name.data,
                password=hash_password(form.password.data))
				# log the user in on signup --> will likely be changed with account activation option 
            login_user(user)
            return redirect(request.args.get('next') or url_for('meeting.home'))
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
			#user login -> find email in db, check hash to verify password
        user = user_datastore.find_user(email=form.email.data)
        if user is not None:
            if verify_password(form.password.data, user.password):
                login_user(user)
                flash('Logged in successfully, {}'.format(user.name))
                return redirect(request.args.get('next') or url_for('meeting.home'))
    flash('Invalid Email or Password')
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('logged out')
    return redirect(url_for('auth.login'))
