from flask import Blueprint, render_template, flash, request, redirect, url_for

search = Blueprint('search', __name__)


@search.route('/users')
def user():
	return render_template('search/users.html')