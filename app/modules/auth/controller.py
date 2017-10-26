from app.modules.auth.model import User, SignupForm, LoginForm, PasswordReset, \
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
            #the following email 
            mail.send_email(
                from_email='quillio.admin@quillio.com', 
                to_email=form.email.data, 
                subject='Welcome to Quillio',
				html=get_html(form.name.data, activation_token, form.email.data)
            )
            return render_template('auth/activation_request.html')
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
            if verify_password(form.password.data, user.password) and user.active:
                login_user(user)
                flash('Logged in successfully, {}'.format(user.name))
                return redirect(request.args.get('next') or url_for('meeting.home'))
    flash('Invalid Email or Password')
    return redirect(url_for('auth.login'))


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = PasswordReset(request.form)
    if request.method == 'GET':
        return render_template('auth/password_reset_request.html', form=form)

    if form.validate():
        #do the shits here
        user = user_datastore.find_user(email=form.email.data)
        if user is not None:
            #generate token, save the hash, send the email with token and email as params
            reset_token = secrets.token_urlsafe(32)
            hash_reset = hash_password(reset_token)
            user.password_reset_hash = hash_reset
            mail.send_email(
                from_email='quillio.admin@quillio.com', 
                to_email=user.email, 
                subject='Welcome to Quillio',
				html=password_html(form.name.data, activation_token, form.email.data)
            )
            return render_template('auth/reset_confirmation.html')
    flash('This email is not registered in our system. Please create an account.')
    return redirect(url_for('auth.signup'))

@auth.route('/reset_password/<reset_hash>/<email_param>', methods=['GET', 'POST'])
def reset_password(reset_hash, email_param):
    user = user_datastore.find_user(email=email_param)
    if user is not None:
        if verify_password(rest_hash, user.password_reset_hash):
            #let user go to password reset page
            return redirect(url_for('auth.reset_form'))
    flash("error Invalid password reset link provided. Please sign in.")
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('logged out')
    return redirect(url_for('auth.login'))

@auth.route('/activate_account/<activation_hash>/<email_param>', methods=['GET','POST'])
def activate_account(activation_hash, email_param):
    #method is used to activate a user's account following the email notification they receive upon signup
    user = user_datastore.find_user(email=email_param)
    if user is not None:
        if verify_password(activation_hash, user.activation_hash):
            user.acitve = True
            login_user(user)
            flash("success Successfully activated account!")
            return redirect(url_for('meeting.home'))
    flash("error Invalid email or activation link!")
    return redirect(url_for('auth.signup'))

#the following method generates the html template for the email notification
def get_html(name, token, email_data):
    header='<nav style="height:50px" class="navbar navbar-expand-lg pkColor"></nav><h2 align="center">Account Activation</h2>'
    body='<p>Dear '+name+',</p><br><p>Welcome to Quillio! To activate your account, please follow the following link:</p>'
    link='<a href=http://0.0.0.0:5000'+url_for('auth.activate_account', activation_hash=token, email_param=email_data)+'>Activate account</a></br>'
    close='<p>Thanks!</p><br><p>The Quillio Team</p>'
    to_ret=(header+body+link+close)
    return to_ret
def password_html(name, token, email_data):
    header='<nav style="height:50px" class="navbar navbar-expand-lg pkColor"></nav><h2 align="center">Account Activation</h2>'
    body='<p>Dear '+name+',</p><br><p>We received your request for password reset. If you did not request to reset your password, please disregard this email and do not share it with anyone.<p>'
    body2='<p>Follow this link to reset your password: </p><br>'
    link='<a href=http://0.0.0.0:5000'+url_for('auth.reset_password',activation_hash=token, email_param=email_data )+'>Reset Password</a><br>'
    close='<p>Thanks!</p><br><p>The Quillio Team</p>'
    to_ret = (header+body+body2+link+close)
    return to_ret
