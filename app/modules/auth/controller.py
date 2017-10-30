import secrets

from app import app
from app.modules.auth.model import User, SignupForm, LoginForm, mail, \
    user_datastore, PasswordReset

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
            # generate activation token
            activation_token = secrets.token_urlsafe(32)
            token_hash = hash_password(activation_token)

            # add user to the database
            user = user_datastore.create_user(
                email=form.email.data,
                name=form.name.data,
                password=hash_password(form.password.data),
                activation_hash=token_hash,
                active=True,
                authenticated=False
            )

            # send registration email
            mail.send_email(
                from_email=app.config['SENDGRID_DEFAULT_FROM'],
                to_email=form.email.data,
                subject='Welcome to Quillio',
                html=activate_html(form.name.data, activation_token,
                                   form.email.data)
            )
            return render_template('auth/activation_request.html')
        except Exception as e:
            flash('error A Problem has Occured, Please Try Again! {}'.format(e))
            return redirect(url_for('auth.signup'))
    flash('error Invalid Email or Password')
    return redirect(url_for('auth.signup'))


def activate_html(name, token, email_data):
    """ Generates the activation email template """

    header = '<nav style="height:50px" class="navbar navbar-expand-lg pkColor"></nav><h2 align="center">Account Activation</h2>'
    body = '<p>Dear ' + name + \
        ',</p><br><p>Welcome to Quillio! To activate your account, please follow the following link:</p>'
    link = '<a href=http://0.0.0.0:5000' + \
        url_for('auth.activate_account', activation_hash=token,
                email_param=email_data) + '> Activate account </a></br>'
    close = '<p>Thanks!</p><br><p>The Quillio Team</p>'
    to_ret = (header + body + link + close)
    return to_ret


@auth.route('/activate/<activation_hash>/<email_param>', methods=['GET', 'POST'])
def activate_account(activation_hash, email_param):
    """ Activates the user's account.  A user recieves this link after
        signing up.
    """

    user = user_datastore.find_user(email=email_param)
    if user is not None:
        if verify_password(activation_hash, user.activation_hash):
            # authenticate the user
            user.authenticated = True
            user.save()

            login_user(user)
            flash("success Successfully Authenticated account!")
            return redirect(url_for('meeting.home'))
    flash("error Invalid email or activation link!")
    return redirect(url_for('auth.signup'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """ Creates a session for the current user """

    form = LoginForm(request.form)

    if request.method == 'GET':
        return render_template('auth/login.html', form=form)

    if form.validate():
        user = user_datastore.find_user(email=form.email.data)
        if user is not None:
            # validate the user has entered the correct password
            if verify_password(form.password.data, user.password):
                # validate that the user has authenticated their account
                if user.is_authenticated():
                    login_user(user)
                    flash('success Logged in Successfully, {}'.format(user.name))
                    return redirect(request.args.get('next') or url_for('meeting.home'))
                else:
                    # user has not authenticated their account
                    flash('error Please Authenticate Your Account.\n'
                          'You Should Have Received an Email on Signup')
                    return redirect(url_for('auth.login'))
            else:
                flash('error Invalid Password. Please Try Again.')
                return redirect(url_for('auth.login'))
    flash('error Invalid Email. Please Try Again.')
    return redirect(url_for('auth.login'))


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = PasswordReset(request.form)
    if request.method == 'GET':
        return render_template('auth/password_reset_request.html', form=form)

    if form.validate():
        user = user_datastore.find_user(email=form.email.data)
        if user is not None:
            # generate reset token
            reset_token = secrets.token_urlsafe(32)
            hash_reset = hash_password(reset_token)

            # update the user's password reset hash
            user.password_reset_hash = hash_reset
            user.save()

            # send the password reset email
            mail.send_email(
                from_email='quillio.admin@quillio.com',
                to_email=user.email,
                subject='Welcome to Quillio',
                html=password_html(form.name.data, reset_token,
                                   form.email.data)
            )

            return render_template('auth/reset_confirmation.html')
        else:
            flash('error This Email is not Registered in our System.'
                  'Please Create an Account.')
            return redirect(url_for('auth.signup'))
    flash('error Could not Reset Password at this Time.')
    return redirect(url_for('auth.signup'))


@auth.route('/reset_password/<reset_hash>/<email_param>', methods=['GET', 'POST'])
def reset_password(reset_hash, email_param):
    user = user_datastore.find_user(email=email_param)
    if user is not None:
        if verify_password(reset_hash, user.password_reset_hash):
            return redirect(url_for('auth.reset_form'))
    flash("error Invalid password reset link provided. Please sign in.")
    return redirect(url_for('auth.login'))


@auth.route('/reset_form/<email_param>', methods=['GET', 'POST'])
def reset_form(email_param):
    if request.method.request == 'GET':
        return render_template('auth/password_reset.html')
    if form.validate():
        user = user_datastore.find_user(email=email_param)
        if user is not None:
            user.password = hash_password(form.password.data)
            flash("success Password successfully reset!")
            return redirect(url_for('auth.login'))
    flash("error Invalid Password Entered! Please try again.")
    return redirect(url_for('auth.reset_form', email_param=email_param))


def password_html(name, token, email_data):
    """ Generates the password reset email """

    header = '<nav style="height:50px" class="navbar navbar-expand-lg pkColor"></nav><h2 align="center">Account Activation</h2>'
    body = '<p>Dear ' + name + ',</p><br><p>We received your request for password reset. If you did not request to reset your password, please disregard this email and do not share it with anyone.<p>'
    body2 = '<p>Follow this link to reset your password: </p><br>'
    link = '<a href=http://0.0.0.0:5000' + \
        url_for('auth.reset_password', activation_hash=token,
                email_param=email_data) + '>Reset Password</a><br>'
    close = '<p>Thanks!</p><br><p>The Quillio Team</p>'
    to_ret = (header + body + body2 + link + close)
    return to_ret


@auth.route('/logout')
@login_required
def logout():
    """ Deletes the session for the current user """

    logout_user()
    flash('success Successfully Logged Out')
    return redirect(url_for('auth.login'))