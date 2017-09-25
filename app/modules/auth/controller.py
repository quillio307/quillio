from flask import Blueprint
from flask import request, render_template, jsonify

from app.modules.auth.model import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    email = request.form['email']
    password = request.form['password']
    return jsonify({
        'email': email,
        'password': password
        })


@auth.route('/signup', methods=['GET', 'POST'])
def auth_register():
    if request.method == 'GET':
        return render_template('auth/signup.html')
    name = request.form['name']
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    User(name=name, email=email, username=username, password=password).save()
    return jsonify({
        'name': name,
        'email': email,
        'username': username,
        'password': password
        })
