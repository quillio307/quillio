import secrets

from app import app
from app.modules.auth.model import User, SignupForm, LoginForm, mail, \
    user_datastore, PasswordResetRequestForm, PasswordResetForm

from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_security import login_user, logout_user, login_required, \
    current_user
from flask_security.utils import hash_password, verify_password

auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """ Signs the Current User In """

    form = SignupForm(request.form)
    if request.method == 'GET':
        return render_template('auth/signup.html', form=form)

    # user has sent invalid input
    if not form.validate():
        flash('error Invalid Email or Password')
        return redirect(url_for('auth.signup'))

    try:
        # generate activation token
        activation_token = secrets.token_urlsafe(32)

        # send registration email
        mail.send_email(
            from_email=app.config['SENDGRID_DEFAULT_FROM'],
            to_email=form.email.data,
            subject='Welcome to Quillio',
            html=activate_html(form.name.data, activation_token,
                               form.email.data)
        )

        # add user to the database
        user_datastore.create_user(
            email=form.email.data,
            name=form.name.data,
            password=hash_password(form.password.data),
            activation_hash=hash_password(activation_token),
            active=True,
            authenticated=False
        )

        flash('Please Check Your Email For An Activation Request.')
        return redirect(url_for('auth.login'))
    except Exception as e:
        print(str(e))
        flash('error An Error has Occured, Please Try Again!')
        return redirect(url_for('auth.signup'))


@auth.route('/activate/<activation_token>/<email>', methods=['GET'])
def activate_account(activation_token, email):
    """ Activates the user's account.  A user recieves this link after
        signing up. """

    user = user_datastore.find_user(email=email)

    if user is None:
        flash('error Invalid Email, Please Create an Account.')
        return redirect(url_for('auth.signup'))

    if not verify_password(activation_token, user.activation_hash):
        flash('error Could not Validate Activation Token.')
        return redirect(url_for('auth.signup'))

    user.authenticated = True
    user.save()

    login_user(user)
    flash("success Successfully Authenticated account!")
    return redirect(url_for('meetings.home'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """ Creates a session for the current user """

    form = LoginForm(request.form)

    if request.method == 'GET':
        return render_template('auth/login.html', form=form)

    if not form.validate():
        flash('error Invalid Email or Password.')
        return redirect(url_for('auth.login'))

    user = user_datastore.find_user(email=form.email.data)

    # user does not exist
    if user is None:
        flash('error Please Make Sure You Have Created an Account.')
        return redirect(url_for('auth.signup'))

    # user provided invalid password
    if not verify_password(form.password.data, user.password):
        flash('error Invalid Email or Password.')
        return redirect(url_for('auth.login'))

    # user has not authenticated their account
    if not user.is_authenticated():
        flash('error Please Authenticate Your Account.')
        return redirect(url_for('auth.login'))

    login_user(user)

    flash('success Logged in Successfully, {}'.format(user.name))
    return redirect(request.args.get('next') or url_for('meetings.home'))


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """ Initializes a User's Request to Reset their Password """

    form = PasswordResetRequestForm(request.form)

    if request.method == 'GET':
        return render_template('auth/password_reset_request.html', form=form)

    if not form.validate():
        flash('error Could not Reset Password at this Time.')
        return redirect(url_for('auth.signup'))

    user = user_datastore.find_user(email=form.email.data)

    if user is None:
        flash('error Invalid Email. Please Create an Account.')
        return redirect(url_for('auth.signup'))

    # generate reset token
    reset_token = secrets.token_urlsafe(32)

    # update the user's password reset hash
    user.password_reset_hash = hash_password(reset_token)
    user.save()

    try:
        # send the password reset email
        mail.send_email(
            from_email=app.config['SENDGRID_DEFAULT_FROM'],
            to_email=user.email,
            subject='Quillio Reset Password',
            html=password_html(user.name, reset_token, form.email.data)
        )

        flash('success Please Check Your Email For a Reset Confirmation.')
        return redirect(url_for('auth.login'))
    except Exception as e:
        print(str(e))
        flash('error Could Not Send Reset Request.')
        return redirect(url_for('auth.login'))


@auth.route('/reset_password/<reset_token>/<email>', methods=['GET'])
def reset_password(reset_token, email):
    """ Validates the User's Password Reset Request """

    user = user_datastore.find_user(email=email)

    if user is None:
        flash('error Unable To Process Reset Request. Please Try Agiain.')
        return redirect(url_for('auth.login'))

    if not verify_password(reset_token, user.password_reset_hash):
        flash('error Could not Validate Reset Request. Please Try Again.')
        return redirect(url_for('auth.login'))

    return redirect(url_for('auth.reset_form', email=email))


@auth.route('/reset_form/<email>', methods=['GET', 'POST'])
def reset_form(email):
    """ Reset's the User's Password """

    form = PasswordResetForm(request.form)

    if request.method == 'GET':
        return render_template('auth/password_reset.html', form=form)

    if not form.validate():
        flash("error An Error has Occurred, Please try again.")
        return redirect(url_for('auth.login'))

    user = user_datastore.find_user(email=email)

    if user is None:
        flash('error Could Not Find the Specified User.')
        return redirect(url_for('auth.login'))

    # update the user's password
    user.password = hash_password(form.password.data)
    user.save()

    flash("success Password Successfully Reset!")
    return redirect(url_for('auth.login'))


@auth.route('/invite/<email>', methods=['GET'])
@login_required
def invite_user(email):
    try:
        user = current_user._get_current_object()

        mail.send_email(
            from_email=app.config['SENDGRID_DEFAULT_FROM'],
            to_email=email,
            subject='Come Join Quillio',
            html=invite_html(user.email, email)
        )

        flash('success Invitation Sent.')
    except Exception as e:
        flash('error Could not Create Invitation. {}'.format(e))

    return redirect(request.args.get('next') or url_for('meetings.home'))


@auth.route('/logout')
@login_required
def logout():
    """ Deletes the session for the current user """

    logout_user()
    flash('success Successfully Logged Out')
    return redirect(url_for('auth.login'))


def activate_html(name, token, email):
    """ Generates the Account Authentication Email Template """

    header = '<nav style="height:50px" class="navbar navbar-expand-lg pkColor"></nav><h2 align="center"> Account Activation </h2>'
    body = '<p>Dear ' + name + \
        ',</p><br><p> Welcome to Quillio! To activate your account, please follow the following link: </p>'
    link = '<a href=http://localhost:5000' + \
        url_for('auth.activate_account', activation_token=token,
                email=email) + '> Activate account </a></br>'
    close = '<p> Thanks! </p><br><p> The Quillio Team </p>'
    return str(header + body + link + close)


def password_html(name, token, email):
    """ Generates the Password Reset Email Template """

    header = '<nav style="height:50px" class="navbar navbar-expand-lg pkColor"></nav><h2 align="center">Account Activation</h2>'
    body = '<p>Dear ' + name + ',</p><br><p>We received your request for password reset. If you did not request to reset your password, please disregard this email and do not share it with anyone.<p>'
    body2 = '<p>Follow this link to reset your password: </p><br>'
    link = '<a href=http://localhost:5000' + \
        url_for('auth.reset_password', reset_token=token,
                email=email) + '> Reset Password </a><br>'
    close = '<p>Thanks!</p><br><p>The Quillio Team</p>'
    return header + body + body2 + link + close


def invite_html(user_email, email):
    """ Generates the Invitation Email Template """

    header = '<nav style="height:50px" class="navbar navbar-expand-lg pkColor"></nav><h2 align="center">Account Activation</h2>'
    body = '<p> Dear ' + email + ',</p><br><p>' + user_email + \
        ' has invited you to join us at Quillio. </p><br><p> Come see what we can do for you!</p><br>'
    link = '<a href=http://localhost:5000' + \
        url_for('auth.signup') + '> Create an Account </a><br>'
    close = '<p>Thanks!</p><br><p>The Quillio Team</p>'
    return header + body + link + close
