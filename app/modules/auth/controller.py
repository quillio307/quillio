from app.modules.auth.model import User, SignupForm, LoginForm, \
    user_datastore


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
            flash('error A Problem has Occured, Please Try Again! {}'.format(e))
            return redirect(url_for('auth.signup'))
    flash('error Invalid Email or Password')
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
<<<<<<< HEAD
                flash('Logged in successfully, {}'.format(user.name))
                return redirect(request.args.get('next') or url_for('meetings.home'))
    flash('Invalid Email or Password')
=======
                flash('success Logged in Successfully, {}'.format(user.name))
                return redirect(request.args.get('next') or url_for('meeting.home'))
    flash('error Invalid Email or Password')
>>>>>>> 72b1364719044081134a7cde4f4651e806b1d349
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('success Successfully Logged Out')
    return redirect(url_for('auth.login'))
