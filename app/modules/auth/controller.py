from app.modules.auth.model import User, SignupForm, LoginForm, \
    user_datastore
from app.modules.meeting.controller import meeting
from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_security import login_user, logout_user, login_required
from flask_security.utils import hash_password, verify_password
from app import mail
import secrets


auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    if request.method == 'GET':
        return render_template('auth/signup.html', form=form)
    if form.validate():
        try:
            # add user to the database
            activation_token=secrets.token_urlsafe(32)
            hash_act = hash_password(activation_token)
            user = user_datastore.create_user(
                email=form.email.data,
                name=form.name.data,
                password=hash_password(form.password.data),
                activation_hash=hash_act
                )
				# log the user in on signup --> will likely be changed with account activation option
            #the following email 
            mail.send_email(
                from_email='quillio.admin@quillio.com', 
                to_email=form.email.data, 
                subject='Welcome to Quillio', 
                template_id='43482b8d-1fb1-45cb-85d3-1451c8614703',
				html=get_html(form.name.data, activation_token, form.email.data)
            )
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

@auth.route('/activate_account/<activation_hash>/<email_param>', methods=['POST'])
def activate_account(activation_hash, email_param):
    #method is used to activate a user's account following the email notification they receive upon signup
    user = user_datastore.find_user(email=email_param)
    if user is not None:
        if verify_password(activation_hash, user.activation_hash):
            login_user(user)
            flash("success Successfully activated account!")
            return redirect(url_for('meeting.home'))
    flash("error Invalid email or activation link!")
    return redirect(url_for('auth.signup'))

#the following method generates the html template for the email notification
def get_html(name, token, email_data):
    header='<nav style="height:50px" class="navbar navbar-expand-lg pkColor"></nav><h2 align="center">Account Activation</h2>'
    body='<p>Dear '+name+',</p><br><p>Welcome to Quillio! To activate your account, please follow the following link:</p>'
    link='<a href='+url_for('auth.activate_account', activation_hash=token, email_param=email_data)+'>Activate account</a></br>'
    close='<p>Thanks!</p><br><p>The Quillio Team</p>'
    to_ret=(header+body+link+close)
    return to_ret

