from flask import Blueprint
from flask import request, render_template
from flask import flash, url_for, redirect
from flask_login import login_user, logout_user, login_required
from mongoengine import connect

from app.modules.auth.model import User, SignupForm, LoginForm
from config import login_manager, MONGODB_SETTINGS

connect(MONGODB_SETTINGS['db'], host=MONGODB_SETTINGS['host'])

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
            User(name=form.name.data, email=form.email.data, username=form.username.data, password=form.password.data).save()
            flash('Thanks for joining! Please login to continue.')
        except Exception:
            flash('User already exists.')
        return redirect(url_for('auth.login'))
    flash('Invalid Username or Password')
    return redirect(url_for('auth.signup'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'GET':
        return render_template('auth/login.html', form=form)
    if form.validate():
        username = form.username.data
        query = User.objects(username__exact=username)
        if len(query) != 0:
            user = query[0]
            if user.password == form.password.data:
                login_user(user)
                flash('Logged in successfully, {}'.format(user.get_id()))
                return redirect(request.args.get('next') or url_for('home'))
    flash('Invalid Username or Password')
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
