from flask import Blueprint, render_template, flash, request, redirect, url_for

from app.modules.auth.model import User
from app.modules.search.model import SearchForm

search = Blueprint('search', __name__)


@search.route('/users', methods=['GET', 'POST'])
def user():
    form = SearchForm(request.form)
    if request.method == 'GET':
        return render_template('search/users.html')

    if form.validate():
        user = User.objects(email__exact=form.email.data)
        if len(user) == 1:
            flash('Found {}'.format(user[0].name))
        if len(user) == 0:
            flash('User Not Found!')

    return redirect(url_for('search.user'))
