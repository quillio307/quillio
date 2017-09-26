from flask import Blueprint
from flask import render_template, flash
from flask import request, redirect, url_for
from flask_security import login_user, logout_user, \
    login_required

from app.modules.auth.model import SignupForm, LoginForm
from app.modules.auth.model import User
from app.modules.auth.model import user_datastore
from app.setup import login_manager

auth = Blueprint('auth', __name__)


@login_manager.user_loader
def user_loader(user_id):
    """ Reloads the user object from the user ID stored in the session. """
    query = User.objects(id__exact=user_id)
    if len(query) == 0:
        return None
    return query[0]


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
                                        password=form.password.data)

            # set the user to have unregistered and default permissions
            unreg = user_datastore.find_or_create_role('unregistered')
            default = user_datastore.find_or_create_role('default')
            user_datastore.add_role_to_user(user, unreg)
            user_datastore.add_role_to_user(user, default)

            login_user(user)
            return redirect(request.args.get('next') or url_for('home'))
        except Exception as e:
            flash('A Problem has Occured, Please Try Again!')
        return redirect(url_for('auth.signup'))
    flash('Invalid Email or Password')
    return redirect(url_for('auth.signup'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'GET':
        return render_template('auth/login.html', form=form)
    if form.validate():
        email = form.email.data
        query = User.objects(email__exact=email)
        if len(query) != 0:
            user = query[0]
            if user.password == form.password.data:
                login_user(user)
                flash('Logged in successfully, {}'.format(user.get_id()))
                return redirect(request.args.get('next') or url_for('home'))
    flash('Invalid Email or Password')
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
